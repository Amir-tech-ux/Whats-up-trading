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
        "text": text
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        logging.info(
            f"Telegram response: {response.status_code} {response.text}"
        )
        if response.status_code != 200:
            logging.error(f"Failed to send message: {response.text}")
    except Exception as e:
        logging.exception(f"Error while sending message: {e}")

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
        text = str(data["message"].get("text", "")).strip()

        if chat_id is None:
            return jsonify({"status": "no chat id"}), 200

        # נוריד רווחים ונעבוד שורתית
        lines = [
            line.strip().lower()
            for line in text.splitlines()
            if line.strip()
        ]

        logging.info(f"Parsed lines: {lines}")

        # פקודות בסיסיות
        if "/start" in lines:
            send_message(chat_id, "הבוט פעיל! ✅")
        elif ("/ping" in lines or "פינג" in lines or
              "/בדיקה" in lines or "בדיקה" in lines):
            send_message(chat_id, "PONG ✅")
        else:
            # אקו – מחזיר מה שנשלח
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