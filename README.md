# CUHK Duo Bypass

This project provides a mechanism to approve Duo Push security requests without requiring the Duo Mobile app on a phone, specifically tailored for CUHK (Chinese University of Hong Kong) students. It automates the generation of the necessary cryptographic responses to bypass the manual push notification process.

**Disclaimer:** This tool is intended for educational purposes and personal convenience only. Use it responsibly and in accordance with CUHK's IT policies.

## Features
- Approve Duo Push requests automatically.
- No need for a mobile device or the Duo Mobile app.
- Can be deployed on a remote Linux server to act as a persistent authenticator.

## Prerequisites

It is highly recommended to use a cloud server to keep the service running 24/7. **Azure for Students** is a great choice as it provides $100 in free credit and free tier services.

### Setting up an Azure Virtual Machine (Always On)
1. **Register for Azure for Students:** 
   - Go to the [Azure for Students page](https://azure.microsoft.com/en-us/free/students/) and click "Start free".
   - Sign in with your university email address to verify your student status and claim your $100 credit.
2. **Create a Virtual Machine:**
   - In the Azure Portal, search for "Virtual Machines" and click "Create".
   - Choose an **Ubuntu Server** image (e.g., Ubuntu Server 22.04 LTS).
   - Select a low-cost size like `Standard_B1s`.
   - Set up SSH key access or password for your admin account.
   - **Crucial Setting for 24/7 uptime:** During the VM creation process, go to the **"Management"** tab and ensure that **"Enable auto-shutdown" is UNCHECKED**. This guarantees your server runs indefinitely without shutting down automatically.
3. **Connect to your VM:** Use SSH to log in to your newly created Ubuntu server.

Once you are connected to your blank Linux server, you will need to install Git and Docker.

### 1. Update your system
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Git and Docker
```bash
sudo apt-get install -y git docker.io
```

## Installation & Usage

Since this project provides a `Dockerfile`, it is recommended to run it exclusively via Docker to keep your server environment clean.

### 1. Clone the repository
```bash
git clone https://github.com/Jcs6995/cuhk-duo-bypass.git
cd cuhk-duo-bypass
```

### 2. Build the Docker image
```bash
sudo docker build -t cuhk-duo-bypass .
```

### 3. Run the container
```bash
sudo docker run -it --name duo-bypass cuhk-duo-bypass
```

### 4. Setup Duo Bypass
- Go to the [CUHK Duo Device Management Portal](https://duo.itsc.cuhk.edu.hk/portal/Device) to start the process of adding a new device.
- **click the "Tablet" button**. Proceed through the setup until you see the QR code.
- Scan the QR code or send the email. Then, click the link and you will see the activation code.
- Enter this activation code when the running container's script prompts it.
- The script will handle the cryptographic exchange and register itself.
- **Leave the container running 24/7:** To exit the terminal session without killing the Docker container, use the detach command: press `Ctrl + P` followed by `Ctrl + Q` on your keyboard. This leaves everything running quietly in the background.


### 5. Login
- Click "Other options" and then send the Duo push to Android.
