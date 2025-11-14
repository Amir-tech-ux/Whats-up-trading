import os
from flask import Flask, request
import requests

app = Flask(__name__)

# הטוקן נלקח רק מה-ENV ברנדר (לא בקוד)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# פונקציית שליחת הודעה
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# נקודת ה-WebHook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # פקודת בדיקה
        if text == "/start":
            send_message(chat_id, "הבוט פעיל! ✔️")
        elif text == "/ping":
            send_message(chat_id, "PONG ✔️")
        else:
            send_message(chat_id, f"קיבלתי: {text}")

    return "ok", 200

# דף הבית (בדיקה)
@app.route("/")
def home():
    return "Bot is running ✔️"