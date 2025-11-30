from flask import Flask, request
import requests
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_SECRET = "amir404secret"  # שמור על הסוד הזה ב־Webhook URL
app = Flask(__name__)

# מסך הבית – רק לוודא שהשרת חי
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

# הנקודה הקריטית – כאן טלגרם שולח את ההודעות
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "No data", 400

    # טיפול בהודעות טקסט רגילות
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        send_message(chat_id, f"קיבלתי: {text}")

    return "ok", 200


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)