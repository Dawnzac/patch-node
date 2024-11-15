#!/bin/bash

# Check if Google Chrome is already installed
if command -v google-chrome &> /dev/null; then
    echo "Google Chrome is already installed. Checking for updates..."
else
    echo "Google Chrome not found. Installing Google Chrome..."
fi

# Update package list
echo "Updating package list..."
sudo apt update -y

# Download the latest Google Chrome .deb package
echo "Downloading the latest Google Chrome package..."
wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install the downloaded package
echo "Installing Google Chrome..."
sudo apt install -y /tmp/google-chrome-stable_current_amd64.deb

# Verify installation
if command -v google-chrome &> /dev/null; then
    echo "Google Chrome has been successfully installed or updated."
else
    echo "Failed to install Google Chrome."
    exit 1
fi

# Clean up the downloaded .deb package
echo "Cleaning up..."
rm /tmp/google-chrome-stable_current_amd64.deb

echo "Installation script completed."
