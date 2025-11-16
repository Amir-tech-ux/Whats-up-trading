import os
import logging
from flask import Flask, request, jsonify
import requests

# ---------- App ----------
app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# ---------- Telegram Token ----------
TOKEN = (
    os.environ.get("TELEGRAM_BOT_TOKEN")
    or os.environ.get("BOT_TOKEN")
    or os.environ.get("TELEGRAM_TOKEN")
)

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN / BOT_TOKEN / TELEGRAM_TOKEN is not set")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ---------- Helper: send message ----------
def send_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            logging.error(
                "Failed to send message. Status: %s, Body: %s",
                resp.status_code,
                resp.text,
            )
    except Exception as e:
        logging.exception(f"Exception while sending message: {e}")

# ---------- Routes ----------
@app.route("/", methods=["GET"])
def index():
    return "OK – Amir bot is running", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return jsonify({"status": "no chat or text"}), 200

    t = text.lower()

    if t in ("/start", "start", "התחל"):
        reply = "היי אמיר, הבוט מחובר ועובד ✅"
    elif t in ("/ping", "ping", "ping/"):
        reply = "Pong ✅"
    else:
        reply = f"קיבלתי: {text}"

    send_message(chat_id, reply)
    return jsonify({"status": "ok"}), 200