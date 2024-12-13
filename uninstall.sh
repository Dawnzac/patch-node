#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Please use 'sudo'."
    exit 1
fi

set -e
echo "Starting agent uninstallation..."

AGENT_DIR="/opt/patchnode"
SERVICE_FILE="/etc/systemd/system/agent.service"

if systemctl is-active --quiet agent; then
    echo "Stopping the agent service..."
    systemctl stop agent
fi

if systemctl is-enabled --quiet agent; then
    echo "Disabling the agent service..."
    systemctl disable agent
fi

if [ -f "$SERVICE_FILE" ]; then
    echo "Removing the systemd service file..."
    rm -f "$SERVICE_FILE"
fi

echo "Reloading systemd daemon..."
systemctl daemon-reload

# Remove the agent directory
if [ -d "$AGENT_DIR" ]; then
    echo "Removing the agent directory..."
    rm -rf "$AGENT_DIR"
fi

echo "Agent uninstallation complete."
