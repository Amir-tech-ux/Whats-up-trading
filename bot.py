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

# ---------- Helper: send message ----------
def send_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"Failed to send message: {e}")

# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    if "message" in data:
        chat = data["message"].get("chat", {})
        chat_id = chat.get("id")
        text = data["message"].get("text", "")

        if chat_id is None:
            return jsonify({"status": "no chat id"}), 200

        # Normalize text
        lower = text.strip().lower()

        # ----- Commands -----
        if "start" in lower:
            send_message(chat_id, "הבוט פעיל! ✔️")

        elif "ping" in lower or "פינג" in lower or "בדיקה" in lower:
            send_message(chat_id, "PONG ✔️")

        else:
            # Echo
            send_message(chat_id, f"קיבלתי: {text}")

    # Quick OK response
    return jsonify({"status": "ok"}), 200

# ---------- Home page ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✔️", 200

# ---------- Local run (not used on Render) ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)