#!/data/data/com.termux/files/usr/bin/bash

# Driveload Installer
echo -e "\033[1;34m"
echo "   ____                    _       _      "
echo "  |  _ \ _ __ _   _ _ __ | | ___ | |__   "
echo "  | | | | '__| | | | '_ \| |/ _ \| '_ \  "
echo "  | |_| | |  | |_| | |_) | | (_) | |_) | "
echo "  |____/|_|   \__, | .__/|_|\___/|_.__/  "
echo "              |___/|_|                   "
echo -e "\033[0m"

# Colors
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

echo -e "${BLUE}[*] Installing Driveload...${NC}"

# Update packages
echo -e "${GREEN}[+] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

# Install dependencies
echo -e "${GREEN}[+] Installing dependencies...${NC}"
pkg install -y python git wget || {
    echo -e "${RED}[-] Failed to install packages${NC}"
    exit 1
}

# Install Python modules
echo -e "${GREEN}[+] Installing Python modules...${NC}"
pip install --upgrade pip gdown beautifulsoup4 requests || {
    echo -e "${RED}[-] Failed to install Python modules${NC}"
    exit 1
}

# Setup storage
echo -e "${GREEN}[+] Setting up storage...${NC}"
if [ ! -d ~/storage ]; then
    termux-setup-storage || {
        echo -e "${RED}[-] Failed to setup storage${NC}"
        exit 1
    }
fi

# Create download directory
echo -e "${GREEN}[+] Creating download directory...${NC}"
mkdir -p ~/storage/downloads/Driveload

# Make script executable
echo -e "${GREEN}[+] Setting permissions...${NC}"
chmod +x driveload.py

# Create alias
echo -e "${GREEN}[+] Creating driveload command...${NC}"
echo 'alias driveload="python ~/Driveload/driveload.py"' >> ~/.bashrc
echo 'echo "Driveload Commands:"' >> ~/.bashrc
echo 'echo "  driveload <url>          - Download from Google Drive"' >> ~/.bashrc
echo 'echo "  driveload <url> -d <dir> - Custom download location"' >> ~/.bashrc

# Refresh shell
source ~/.bashrc

echo -e "\n${GREEN}[+] Driveload installed successfully!${NC}"
echo -e "${YELLOW}[*] Usage: driveload <Google-Drive-URL>${NC}"
echo -e "${YELLOW}[*] Example: driveload https://drive.google.com/drive/folders/ABC123${NC}"
