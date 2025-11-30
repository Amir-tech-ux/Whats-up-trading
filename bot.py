import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- Load Telegram token from Render env var ---
TOKEN = os.getenv("TELEGRAM_TOKEN")


# --- Send message back to user ---
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    r = requests.post(url, json=payload)
    print("sendMessage status:", r.status_code, r.text)


# --- Webhook route ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # GET – בשביל בדיקה בדפדפן וברנדר
    if request.method == 'GET':
        return "Webhook OK", 200

    # POST – עדכון אמיתי מטלגרם
    data = request.get_json(silent=True, force=True)
    print("Incoming update:", data)

    if not data:
        return "No data", 400

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"You said: {text}"
        send_message(chat_id, reply)

    return "OK", 200


# --- Health check for Render ---
@app.route('/', methods=['GET'])
def home():
    return "Bot is running!", 200


# --- Run server ---
if __name__ == "__main__":
    # Render נותן PORT כמשתנה סביבה, נשתמש בו או ב-10000
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)