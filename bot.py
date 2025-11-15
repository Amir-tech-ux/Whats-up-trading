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
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    requests.post(url, json=payload)

# ---------- Webhook ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    # אם הגיע ריק – מחזירים תשובה מיד
    if not data:
        return jsonify({"status": "no data"}), 200

    if "message" in data:
        chat = data["message"].get("chat", {})
        chat_id = chat.get("id")
        text = data["message"].get("text", "")

        if chat_id is None:
            return jsonify({"status": "no chat id"}), 200

        lower = text.lower()

        if lower == "/start":
            send_message(chat_id, "הבוט פעיל! ✔️")
        elif lower == "/ping" or lower == "פינג" or lower == "/בדיקה":
            send_message(chat_id, "PONG ✔️")
        else:
            # אקו – מחזיר מה שנשלחת
            send_message(chat_id, f"קיבלתי: {text}")

    # תשובה מהירה לטלגרם כדי שלא יהיה timeout
    return jsonify({"status": "ok"}), 200

# ---------- Home page (בדיקה בדפדפן) ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅", 200

# ---------- Local run only (לא בשימוש ברנדר) ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)