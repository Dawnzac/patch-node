#!/bin/bash

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
echo "Updating Homebrew..."
brew update

# Check if Google Chrome is already installed via Homebrew
if brew list --cask google-chrome &> /dev/null; then
    echo "Google Chrome is already installed. Updating to the latest version..."
    brew upgrade --cask google-chrome
else
    echo "Google Chrome not found. Installing Google Chrome..."
    brew install --cask google-chrome
fi

# Verify installation
if brew list --cask google-chrome &> /dev/null; then
    echo "Google Chrome has been successfully installed or updated."
else
    echo "Failed to install Google Chrome."
    exit 1
fi

echo "Installation script completed."
