import os
import sys
import time
import json
import logging
import psutil
import subprocess
import requests
from argparse import ArgumentParser
from datetime import datetime

# logging

logging.basicConfig(filename='/var/log/agent.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_system_info():
    """Collects system information to send to the server."""
    try:
        return {
            "hostname": os.uname()[1],
            "os_version": f"{os.uname().sysname} {os.uname().release}",
            "cpu_load": psutil.getloadavg(),
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().used // (1024 ** 2),  # in MB
            "disk_usage": psutil.disk_usage('/').used // (1024 ** 2)  # in MB
        }
    except Exception as e:
        logging.error(f"Error gathering system information: {e}")
        return {}

def send_report(server_url, auth_token, data):
    """Sends the system report to the server."""
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(f"{server_url}/api/report", headers=headers, json=data, verify=False)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logging.info(f"Report sent successfully: {data}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to send report: {e}")
        return False

def fetch_commands(server_url, auth_token):
    """Fetches commands from the server and returns them."""
    command_url = f"{server_url}/api/commands"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(command_url, headers=headers, verify=False)
        response.raise_for_status()
        commands = response.json()
        logging.info(f"Fetched commands: {commands}")
        return commands
    except requests.RequestException as e:
        logging.error(f"Failed to fetch commands: {e}")
        return None

def execute_command(command):
    """Executes a command or script and returns the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        logging.info(f"Executed command: {command}")
        return {"output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        logging.error(f"Command execution failed: {e}")
        return {"output": "", "error": str(e)}

def report_command_output(server_url, auth_token, hostname, command_result):
    """Reports command execution result back to the server."""
    report_url = f"{server_url}/api/command-result"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    data = {
        "hostname": hostname,
        "result": command_result
    }
    try:
        response = requests.post(report_url, headers=headers, json=data, verify=False)
        response.raise_for_status()
        logging.info("Command result reported successfully.")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to report command result: {e}")
        return False

def main(server_url, auth_token, interval):
    """Main loop to send reports and fetch commands at regular intervals."""
    hostname = os.uname()[1]
    logging.info("Starting agent...")

    while True:
        # Send system report
        system_info = get_system_info()
        system_info['timestamp'] = datetime.utcnow().isoformat()
        
        if system_info:
            send_report(server_url, auth_token, system_info)

        # Fetch and execute commands
        commands = fetch_commands(server_url, auth_token)
        if commands:
            for command in commands.get("commands", []):
                command_result = execute_command(command)
                report_command_output(server_url, auth_token, hostname, command_result)

        # Wait before next report
        time.sleep(interval)

if __name__ == "__main__":
   
    parser = ArgumentParser(description="Agent script to send system reports to a server.")
    parser.add_argument("--server", required=True, help="The server URL to send reports to.")
    parser.add_argument("--token", required=True, help="The authentication token for server access.")
    parser.add_argument("--interval", type=int, default=600, help="Report interval in seconds (default: 600s).")

    args = parser.parse_args()

    main(args.server, args.token, args.interval)
