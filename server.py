from flask import Flask, request, jsonify
from datetime import datetime
import logging

app = Flask(__name__)


logging.basicConfig(filename='agent_reports.log', level=logging.INFO, format='%(asctime)s - %(message)s')
# in-memory storage for reports and commands testing
reports = {}
commands = ["echo 'Hello, Agent!'", "uptime"]

AUTH_TOKEN = "your_secure_token"

def is_authorized(request):
    token = request.headers.get("Authorization")
    return token == f"Bearer {AUTH_TOKEN}"

@app.route('/api/report', methods=['POST'])
def report_status():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Received data: {data}")  # Debugging

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
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(reports), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
