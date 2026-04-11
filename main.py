import time
import pathlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
import urllib.parse
import io
import base64
import datetime
import email.utils
import json
import requests
import sys

class Client:
    def __init__(self, akey=None, pkey=None, host=None, code=None, response=None, keyfile=None):
        if keyfile:
            self.import_key(keyfile)
        else:
            self.pubkey = RSA.generate(2048)

        self.pkey = pkey
        self.akey = akey
        self.host = host
        self.info = {}

        if code:
            self.read_code(code)
        if response:
            self.import_response(response)

    def import_key(self, keyfile):
        if issubclass(type(keyfile), io.IOBase):
            self.pubkey = RSA.import_key(keyfile.read())
        else:
            try:
                self.pubkey = RSA.import_key(keyfile)
            except ValueError:
                with open(keyfile, "rb") as f:
                    self.pubkey = RSA.import_key(f.read())

    def export_key(self, file):
        if type(file) is str:
            with open(file, "wb") as f:
                f.write(self.pubkey.export_key("PEM"))
        else:
            file.write(self.pubkey.export_key("PEM"))

    def read_code(self, code):
        code, host = map(lambda x: x.strip("<>"), code.split("-"))
        missing_padding = len(host) % 4
        if missing_padding:
            host += '=' * (4 - missing_padding)
        self.code = code
        self.host = base64.decodebytes(host.encode("ascii")).decode('ascii')

    def import_response(self, response):
        if type(response) is str:
            with open(response, "r") as f:
                response = json.load(f)
        if "response" in response:
            response = response["response"]
        self.info = response
        if self.host and ("host" not in self.info or not self.info["host"]):
            self.info["host"] = self.host
        elif not self.host and ("host" in self.info and self.info["host"]):
            self.host = self.info["host"]

        # Safe extraction to prevent NoneType errors later
        self.akey = response.get("akey")
        self.pkey = response.get("pkey")

    def export_response(self):
        if self.host and ("host" not in self.info or not self.info["host"]):
            self.info["host"] = self.host
        with open("response.json", 'w') as f:
            json.dump(self.info, f)

    def activate(self):
        try:
            if self.code:
                params = {
                    "customer_protocol": "1",
                    "pubkey": self.pubkey.publickey().export_key("PEM").decode('ascii'),
                    "pkpush": "rsa-sha512",
                    "jailbroken": "false",
                    "architecture": "arm64",
                    "region": "US",
                    "app_id": "com.duosecurity.duomobile",
                    "full_disk_encryption": "true",
                    "passcode_status": "true",
                    "platform": "Android",
                    "app_version": "4.110.0",
                    "app_build_number": "411000",
                    "version": "14",
                    "manufacturer": "unknown",
                    "language": "en",
                    "model": "Browser Extension",
                    "security_patch_level": "2026-04-01"
                }

                print(f"Attempting to activate against {self.host}...")
                r = requests.post(f"https://{self.host}/push/v2/activation/{self.code}", params=params)
                response = r.json()

                # Check if Duo rejected us
                if "stat" in response and response["stat"] != "OK":
                    print("\n" + "="*50)
                    print("🚨 DUO REJECTED THE ACTIVATION 🚨")
                    print(f"Reason: {json.dumps(response, indent=2)}")
                    print("="*50 + "\n")
                    return False

                self.import_response(response)
                return True
            else:
                print("Code is null")
                return False
        except Exception as e:
            print(f"Error during activation: {e}")
            return False

    def generate_signature(self, method, path, time, data):
        if not self.pkey:
            return None
        try:
            message = (time + "\n" + method + "\n" + self.host.lower() + "\n" +
                       path + '\n' + urllib.parse.urlencode(data)).encode('ascii')
            h = SHA512.new(message)
            signature = pkcs1_15.new(self.pubkey).sign(h)
            auth = ("Basic "+base64.b64encode((self.pkey + ":" +
                    base64.b64encode(signature).decode('ascii')).encode('ascii')).decode('ascii'))
            return auth
        except Exception as e:
            print(f"Error generating signature: {e}")
            return None

    def get_transactions(self):
        try:
            dt = datetime.datetime.utcnow()
            time = email.utils.format_datetime(dt)
            path = "/push/v2/device/transactions"
            data = {"akey": self.akey, "fips_status": "1",
                    "hsm_status": "true", "pkpush": "rsa-sha512"}

            signature = self.generate_signature("GET", path, time, data)
            if not signature:
                return {}

            r = requests.get(f"https://{self.host}{path}", params=data, headers={
                             "Authorization": signature, "x-duo-date": time, "host": self.host})
            return r.json()
        except Exception as e:
            return {}

    def reply_transaction(self, transactionid, answer):
        try:
            dt = datetime.datetime.utcnow()
            time = email.utils.format_datetime(dt)
            path = "/push/v2/device/transactions/"+transactionid
            data = {"akey": self.akey, "answer": answer, "fips_status": "1",
                    "hsm_status": "true", "pkpush": "rsa-sha512"}

            signature = self.generate_signature("POST", path, time, data)
            if not signature:
                return {}

            r = requests.post(f"https://{self.host}{path}", data=data, headers={
                              "Authorization": signature, "x-duo-date": time, "host": self.host, "txId": transactionid})
            return r.json()
        except Exception as e:
            return {}

def main():
    code = ""
    host = ""
    c = Client()
    key_exists = False

    if pathlib.Path("key.pem").is_file():
        c.import_key("key.pem")
        key_exists = True
    else:
        c.export_key("key.pem")

    if pathlib.Path("response.json").is_file() and key_exists:
        try:
            c.import_response("response.json")
            if not c.akey or not c.pkey:
                raise ValueError("Keys missing from response.json")
        except Exception:
            print("response.json is corrupted or empty. Please delete it and run again.")
            sys.exit(1)

        if code:
            c.read_code(code)
        if not c.host and host:
            c.host = host
    else:
        if not code:
            code = input("Input code:")
        c.read_code(code)
        success = c.activate()
        if not success:
            print("Exiting because activation failed. Delete key.pem and try again with a new code.")
            sys.exit(1)
        c.export_response()

    while True:
        try:
            r = c.get_transactions()
            t = r.get("response", {}).get("transactions", [])
            print("Checking for transactions...")
            if len(t):
                for tx in t:
                    print(f"Approving transaction: {tx['urgid']}")
                    c.reply_transaction(tx["urgid"], 'approve')
                    time.sleep(2)
        except Exception as e:
            pass
        time.sleep(0.5)

if __name__ == "__main__":
    main()