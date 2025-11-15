import os
import logging
from flask import Flask, request, jsonify
import requests

# ---------- App ----------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---------- Telegram Token ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ---------- Helper ----------
def send_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception as e:
        logging.error(f"Send error: {e}")

# ---------- Webhook ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data or "message" not in data:
        return jsonify({"status": "ok"}), 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    lower = text.lower()

    # ------- Commands -------
    if lower in ["/start", "start"]:
        send_message(chat_id, "הבוט פעיל! ✔️")
        return "", 200

    if lower in ["/ping", "ping", "פינג", "/בדיקה", "בדיקה"]:
        send_message(chat_id, "PONG ✔️")
        return "", 200

    # ------- Echo -------
    send_message(chat_id, f"קיבלתי: {text}")
    return "", 200

# ---------- Home ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✔️", 200