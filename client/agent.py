import os
import sys
import time
import json
import logging
import psutil
import requests
from argparse import ArgumentParser
from datetime import datetime

interval = 10
# ogging
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
        response.raise_for_status()
        logging.info(f"Report sent successfully: {data}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to send report: {e}")
        return False

def main(server_url, auth_token, interval):
    """Main loop to send reports at regular intervals."""
    logging.info("Starting agent...")
    while True:
        system_info = get_system_info()
        system_info['timestamp'] = datetime.utcnow().isoformat()
        
        if not system_info:
            logging.warning("No system info collected, skipping report.")
        else:
            success = send_report(server_url, auth_token, system_info)
            if not success:
                logging.warning("Report sending failed, will retry on next interval.")

        time.sleep(interval)

if __name__ == "__main__":
   
    parser = ArgumentParser(description="Agent script to send system reports to a server.")
    parser.add_argument("--server", required=True, help="The server URL to send reports to.")
    parser.add_argument("--token", required=True, help="The authentication token for server access.")

    args = parser.parse_args()

    main(args.server, args.token, interval)
