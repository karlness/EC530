import requests
import threading
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5000"

username = input("Enter your name: ")
last_timestamp = ""

def send_loop():
    while True:
        msg = input()
        if msg.strip() == "":
            continue
        requests.post(f"{API_URL}/send", json={
            "username": username,
            "message": msg
        })

def receive_loop():
    global last_timestamp
    while True:
        try:
            response = requests.get(f"{API_URL}/messages", params={"since": last_timestamp})
            data = response.json()
            if data:
                for msg in data:
                    if msg["username"] != username:
                        print(f"\n[{msg['username']}] {msg['message']}")
                    last_timestamp = msg["timestamp"]
            time.sleep(1)
        except:
            print("Error fetching messages.")
            time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=send_loop, daemon=True).start()
    receive_loop()