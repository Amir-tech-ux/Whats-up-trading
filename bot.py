import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- Load Telegram token ---
TOKEN = os.getenv("TELEGRAM_TOKEN")

# --- Send message back to user ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# --- Webhook route ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return "No data", 400

    # If a regular message arrives
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Simple echo
        send_message(chat_id, f"You said: {text}")

    return "OK", 200

# --- Health check for Render ---
@app.route('/', methods=['GET'])
def home():
    return "Bot is running!", 200

# --- Run server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)