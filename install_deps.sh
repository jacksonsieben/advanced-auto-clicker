#!/bin/bash

echo "Installing dependencies for Advanced Auto Clicker..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed!"
    echo "Please install Python3 using your package manager:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed!"
    echo "Please install pip3 using your package manager"
    exit 1
fi

# Install dependencies
echo "Installing required packages..."
pip3 install -r requirements.txt

# Install PyInstaller for building executable
echo "Installing PyInstaller..."
pip3 install pyinstaller

echo ""
echo "Dependencies installed successfully!"
echo "You can now build the executable by running: ./build_linux.sh"
