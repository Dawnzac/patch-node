from flask import Flask, request,send_file, jsonify
from datetime import datetime
import logging

app = Flask(__name__)


logging.basicConfig(filename='agent_reports.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# in-memory storage for reports and commands testing
reports = {}
commands = ["echo 'Hello, Agent!'", "uptime"]

AUTH_TOKEN = "secure_token"

def is_authorized(request):
    token = request.headers.get("Authorization")
    return token == f"Bearer {AUTH_TOKEN}"

@app.route('/install.sh', methods=['GET'])
def serve_install_script():
    """Serves the agent installation script."""
    try:
        script_path = "install.sh"
        return send_file(script_path, as_attachment=False), 200
    except Exception as e:
        return jsonify({"error": f"Failed to serve the install script: {str(e)}"}), 500


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
