#!/bin/bash

AGENT_DIR="/opt/patchnode"
AGENT_SCRIPT="agent.py"
SERVICE_NAME="agent.service"
SERVER_URL="https://192.168.1.10:5000"  # Replace with your server URL
AUTH_TOKEN="secure_token"            # Replace with your secure token

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install dependencies
echo "Installing dependencies..."
apt update
apt install -y python3 python3-pip

pip3 install requests psutil

# Create the agent directory
echo "Setting up the agent directory..."
mkdir -p $AGENT_DIR

# Copy agent.py to /opt/agent or download it if hosted
if [ -f "./$AGENT_SCRIPT" ]; then
  echo "Copying agent script to $AGENT_DIR..."
  cp $AGENT_SCRIPT $AGENT_DIR/
else
  echo "Downloading agent script from the server..."
  curl -o "$AGENT_DIR/$AGENT_SCRIPT" "$SERVER_URL/$AGENT_SCRIPT"
fi

# Create systemd service file
echo "Creating systemd service..."
cat << EOF > /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=System Reporting Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 $AGENT_DIR/$AGENT_SCRIPT --server $SERVER_URL --token $AUTH_TOKEN
Restart=always
User=patchnode
Environment=SERVER_URL=$SERVER_URL
Environment=AUTH_TOKEN=$AUTH_TOKEN

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, start and enable the service
echo "Enabling and starting the agent service..."
systemctl daemon-reload
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

# Check service status
echo "Agent installation complete. Checking service status..."
systemctl status $SERVICE_NAME
