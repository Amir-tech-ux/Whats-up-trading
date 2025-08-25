 import os
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(name)
logging.basicConfig(level=logging.INFO)

# --- ENV ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")  # לדוגמה: https://your-app.onrender.com
CHAT_ID = os.getenv("CHAT_ID")  # אם יש לך צ'אט קבוע לבדיקות

# --- API ---
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Incoming update: {data}")

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]

            # תשובה אוטומטית
            reply = f"התקבל: {text}"
            send_message(chat_id, reply)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logging.error(f"Error in webhook: {e}")
        return jsonify({"status": "error"}), 500

def send_message(chat_id, text):
    """ שולח הודעה לצ'אט בוט """
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    logging.info(f"Message sent: {response.text}")

if name == "main":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
