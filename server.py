from flask import Flask, request,send_file, jsonify
from datetime import datetime
import logging
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

print("\nServer Name :  " + hostname)
print("Server IP Address :  " + IPAddr + "\n")
print("Run the following command on the host system : \n\n \t curl -s -k https://"+IPAddr+":5000/install.sh | sudo bash\n")
app = Flask(__name__)


logging.basicConfig(filename='agent_reports.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='agent_error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='agent_warn.log', level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
# in-memory storage for reports and commands testing
reports = {}
command_reports = {}
commands = ["echo 'Hello there, It works!'"]

AUTH_TOKEN = "secure_token"

def is_authorized(request):
    token = request.headers.get("Authorization")
    return token == f"Bearer {AUTH_TOKEN}"

# @app.route('/install.sh', methods=['GET'])
# def serve_install_script():
#     """Serves the static agent installation script."""
#     try:
#         script_path = "install.sh"
#         return send_file(script_path, as_attachment=False), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to serve the install script: {str(e)}"}), 500


@app.route('/install.sh', methods=['GET'])
def serve_install_script():
    """Generates and serves the agent installation script dynamically."""
    install_script = f"""#!/bin/bash

        #set -e
        echo "Starting agent installation..."

        AGENT_DIR="/opt/patchnode"
        AGENT_SCRIPT="agent.py"
        SERVICE_FILE="/etc/systemd/system/agent.service"
        SERVER_URL="https://{IPAddr}:5000"  
        AUTH_TOKEN="secure_token"           
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
        #chmod +x "$AGENT_DIR/$AGENT_SCRIPT"
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
    """
    return install_script, 200, {"Content-Type": "text/plain"}



@app.route('/uninstall.sh', methods=['GET'])
def serve_uninstall_script():
    """Serves the agent installation script."""
    try:
        script_path = "uninstall.sh"
        return send_file(script_path, as_attachment=False), 200
    except Exception as e:
        return jsonify({"error": f"Failed to serve the uninstall script: {str(e)}"}), 500
    
@app.route('/agent.py', methods=['GET'])
def serve_agent_script():
    """Serves the agent File."""
    try:
        script_path = "client/agent.py"
        return send_file(script_path, as_attachment=False), 200
    except Exception as e:
        return jsonify({"error": f"Failed to serve the agent script: {str(e)}"}), 500
    
def index():
    """Basic server status check."""
    return jsonify({"message": "Server is running."}), 200

@app.route('/api/report', methods=['POST'])
def report_status():
    if not is_authorized(request):
        logging.warning(f"Invalid token from host: {request.remote_addr}, Token: {AUTH_TOKEN}")
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Received data: {data}")  # Debugging
    logging.info(f"Report received from host: {request.remote_addr}, Data: {data}")
    hostname = data.get("hostname")
    if hostname:
        reports[hostname] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return jsonify({"message": "Report received"}), 200
    return jsonify({"error": "Bad hostname"}), 400


@app.route('/api/commands', methods=['GET'])
def get_commands():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"commands": commands}), 200

@app.route('/api/command', methods=['POST'])
def add_command():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 403

    command = request.json.get("command")
    if command:
        commands.append(command)
        return jsonify({"message": "Command added"}), 200
    return jsonify({"error": "Bad request"}), 400

@app.route('/api/reports', methods=['GET'])
def get_reports():
    if not is_authorized(request):
        logging.warning(f"Invalid token from host: {request.remote_addr}, Token: {AUTH_TOKEN}")
        return jsonify({"error": "Unauthorized"}), 403  

    return jsonify(reports), 200

@app.route('/api/command-result', methods=['POST'])
def command_result():
    if not is_authorized(request):
        logging.warning(f"Invalid token from host: {request.remote_addr}, Token: {AUTH_TOKEN}")
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
   
    if data and "hostname" in data and "result" in data:
        hostname = data["hostname"]
        result = data["result"]
        command_reports[hostname] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        logging.info(f"Received command result from {hostname}: {result}")
        print(f"Received command output : {result}")
        return jsonify({"status": "success", "message": "Command result received"}), 200
    else:
        logging.error("Invalid data received.")
        return jsonify({"status": "failure", "message": "Invalid data received"}), 400

@app.route('/api/command-results', methods=['GET'])
def get_command_results():
    if not is_authorized(request):
        logging.warning(f"Invalid token from host: {request.remote_addr}, Token: {AUTH_TOKEN}")
        return jsonify({"error": "Unauthorized"}), 403  

    return jsonify(command_reports), 200


@app.route('/api/command', methods=['DELETE'])
def delete_command():
    """Delete a command from the list."""
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 403

    command = request.json.get("command")
    if command in commands:
        commands.remove(command)
        return jsonify({"message": "Command deleted"}), 200
    return jsonify({"error": "Command not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
