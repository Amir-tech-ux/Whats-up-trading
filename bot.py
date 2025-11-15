import os
from flask import Flask, request
import requests

app = Flask(__name__)

# טוקן הבוט מטלגרם
TOKEN = "8101329393:AAGZgiQfG0xwI-k3pc4QG__5VDFcIom5Zyg"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# פונקציה לשליחת הודעה
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] sending message: {e}")

# נקודת ה-Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming update:", data)

    if not data:
        return "no data", 400

    message = data.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "")

    chat_id = chat.get("id")
    if not chat_id:
        return "no chat id", 200

    # פקודות בדיקה
    if text == "/start":
        send_message(chat_id, "הבוט פעיל! ✅")
    elif text == "/ping":
        send_message(chat_id, "PONG ✅")
    else:
        send_message(chat_id, f"✔ קיבלתי: {text}")

    return "ok", 200

# דף הבית (בדיקה)
@app.route("/")
def home():
    return "Bot is running ✅"

# להרצה לוקאלית (לא חובה ברנדר)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)