import os
from flask import Flask, request
import requests

app = Flask(__name__)

# --- TOKEN ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# --- SEND MESSAGE ---
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# --- WEBHOOK ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data", 200

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "/start":
            send_message(chat_id, "הבוט פעיל! ✔")
        elif text.lower() == "/ping":
            send_message(chat_id, "PONG ✔")
        else:
            send_message(chat_id, f"קיבלתי: {text}")

    return "ok", 200

# --- HOME PAGE ---
@app.route("/")
def home():
    return "Bot is running ✔"

# --- RUN (for local tests only) ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)