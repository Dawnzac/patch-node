#!/bin/bash

#set -e
echo "Starting agent installation..."

AGENT_DIR="/opt/patchnode"
AGENT_SCRIPT="agent.py"
SERVICE_FILE="/etc/systemd/system/agent.service"
SERVER_URL="https://<ip-addr>:5000"  # Replace with your server URL
AUTH_TOKEN="secure_token"            # Replace with your secure token
AGENT_URL="$SERVER_URL/$AGENT_SCRIPT"

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

if [ ! -d "$AGENT_DIR" ]; then
    mkdir -p "$AGENT_DIR"
    echo "Created directory $AGENT_DIR."
fi

curl -s -k -o "$AGENT_DIR/$AGENT_SCRIPT" "$AGENT_URL"
chmod +x "$AGENT_DIR/$AGENT_SCRIPT"
echo "Downloaded and set up $AGENT_SCRIPT."

# Install dependencies
echo "Installing dependencies..."
#apt update
#apt install -y python3 python3-pip

pip3 install requests psutil --quiet

# Create systemd service file
echo "Creating systemd service..."
cat << EOF > $SERVICE_FILE
[Unit]
Description=Patchnode Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 $AGENT_DIR/$AGENT_SCRIPT --server $SERVER_URL --token $AUTH_TOKEN
Restart=always
User=root
Environment=SERVER_URL=$SERVER_URL
Environment=AUTH_TOKEN=$AUTH_TOKEN

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, start and enable the service
echo "Enabling and starting the agent service..."
systemctl daemon-reload
systemctl start agent
systemctl enable agent

# Check service status
echo "Agent installation complete. Checking service status..."
systemctl status agent
