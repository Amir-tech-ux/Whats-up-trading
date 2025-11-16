import os
import logging
import requests
from flask import Flask, request

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ---------- Telegram Token ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        logging.info(f"Sending message to {chat_id}: {text}")
        resp = requests.post(url, json=payload, timeout=5)
        logging.info(f"Telegram response: {resp.status_code} {resp.text}")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    logging.info(f"Incoming update: {data}")

    msg = (
        data.get("message")
        or data.get("edited_message")
        or data.get("channel_post")
        or data.get("edited_channel_post")
    )
    if not msg:
        return "no message", 200

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    text = msg.get("text", "") or ""

    if not chat_id:
        logging.info("No chat_id")
        return "no chat_id", 200

    send(chat_id, f"✅ קיבלתי: {text}")
    return "ok", 200


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)