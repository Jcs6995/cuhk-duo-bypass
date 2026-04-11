# CUHK Duo Bypass

This project provides a mechanism to approve Duo Push security requests without requiring the Duo Mobile app on a phone, specifically tailored for CUHK (Chinese University of Hong Kong) students. It automates the generation of the necessary cryptographic responses to bypass the manual push notification process.

**Disclaimer:** This tool is intended for educational purposes and personal convenience only. Use it responsibly and in accordance with CUHK's IT policies.

## Features
- Approve Duo Push requests automatically.
- No need for a mobile device or the Duo Mobile app.
- Can be deployed on a remote Linux server to act as a persistent authenticator.

## Prerequisites

Assuming you are starting with a completely blank Linux server (e.g., Ubuntu/Debian), you will need to install Git and Docker.

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
- When the container starts running, the script will prompt you for an activation code.
- You can obtain this code from the Duo activation QR code (using a generic QR code scanner) or by copying the link provided in your Duo setup email.
- The script will handle the cryptographic exchange and register itself.
- From then on, leave the container running. It will wait for authentication requests and automatically approve them without needing your phone.
