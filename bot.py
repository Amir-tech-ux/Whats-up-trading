import os
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---- Telegram Config ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN / BOT_TOKEN is not set")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---- Send Message ----
def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "text": text
    })

# ---- Webhook route ----
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"status": "no data"}), 200

    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat")
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        return jsonify({"status": "no chat id"}), 200

    normalized = text.strip().lower()

    # ---- Commands ----
    if normalized == "/start":
        reply = "היי אמיר! הבוט מחובר ומוכן ✔️"
    elif normalized == "/ping":
        reply = "pong ✔️ הבוט חי 🙂"
    else:
        reply = f"קיבלתי ממך:\n{text}\nההודעה הגיעה לשרת ✔️"

    send_message(chat_id, reply)
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✔️", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)