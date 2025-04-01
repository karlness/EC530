from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
messages = []

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    username = data.get("username")
    text = data.get("message")
    timestamp = datetime.utcnow().isoformat()

    if not username or not text:
        return jsonify({"error": "Missing fields"}), 400

    message = {"username": username, "message": text, "timestamp": timestamp}
    messages.append(message)
    return jsonify({"status": "Message received"}), 200

@app.route("/messages", methods=["GET"])
def get_messages():
    since = request.args.get("since")
    if since:
        filtered = [msg for msg in messages if msg["timestamp"] > since]
    else:
        filtered = messages
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
