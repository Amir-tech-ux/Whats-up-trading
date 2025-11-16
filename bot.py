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
        resp = requests.post(url, json=payload, timeout=5)
        if not resp.ok:
            logging.error(
                "Telegram API error %s: %s",
                resp.status_code,
                resp.text
            )
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    # קח את ההודעה הרלוונטית (message או edited_message)
    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if chat_id is None:
        return jsonify({"status": "no chat id"}), 200

    # Normalize text
    lower = (text or "").strip().lower()

    # להסיר "/" אם יש /start /ping וכו'
    if lower.startswith("/"):
        lower = lower[1:]

    # ----- Commands -----
    if lower == "start":
        send_message(chat_id, "הבוט פעיל! ✔️")
    elif lower in ["ping", "פינג", "בדיקה"]:
        send_message(chat_id, "PONG ✔️")
    else:
        # Echo ברירת מחדל
        send_message(chat_id, f"קיבלתי: {text}")

    # תגובה מהירה ל-Telegram
    return jsonify({"status": "ok"}), 200


# ---------- Home page ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅", 200


# ---------- Local run (לא בשימוש ב-Render, אבל טוב לפיתוח) ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)