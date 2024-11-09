# agent.py
import os
import platform
import requests
import time
import subprocess

SERVER_URL = 'https://172.20.5.10/api/report'
INTERVAL = 3600  # Report every hour

def get_system_info():
    return {
        'hostname': platform.node(),
        'os_version': platform.platform(),
        'cpu_load': os.getloadavg(),
        'memory_usage': subprocess.check_output(['free', '-m']).decode(),
        'disk_usage': subprocess.check_output(['df', '-h']).decode(),
    }

def report_status():
    system_info = get_system_info()
    try:
        response = requests.post(SERVER_URL, json=system_info)
        print(f"Status reported, response code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error reporting status: {e}")

if __name__ == "__main__":
    while True:
        report_status()
        time.sleep(INTERVAL)
