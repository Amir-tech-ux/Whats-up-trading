import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- Load config from environment ---
TOKEN = os.getenv("BOT_TOKEN")
SECRET = os.getenv("WEBHOOK_SECRET")


# --- Helper: send message back to user ---
def send_message(chat_id: int, text: str):
    if not TOKEN:
        print("ERROR: BOT_TOKEN is not set")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("sendMessage status:", r.status_code, r.text)
    except Exception as e:
        print("Error sending message:", e)


# --- Webhook route ---
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # בדיקה קלה דרך דפדפן (GET)
    if request.method == "GET":
        return "Webhook endpoint is alive", 200

    # אימות סיקרט מול טלגרם
    header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if SECRET and header_secret != SECRET:
        print("Invalid secret token:", header_secret)
        return "Unauthorized", 401

    data = request.get_json(silent=True)
    print("Incoming update:", data)

    if not data:
        return "No data", 400

    # הודעה רגילה
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # תשובה פשוטה /start / ping וכו'
        if text.lower() in ["/start", "start"]:
            reply = "היי אמיר, הבוט ברנדר מחובר ועובד ✅"
        elif text.lower() in ["/ping", "ping", "ping/"]:
            reply = "pong ✅ (מ־Render)"
        else:
            reply = f"You said: {text}"

        send_message(chat_id, reply)

    return "OK", 200


# --- Health check for Render ---
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200


# --- Run server ---
if __name__ == "__main__":
    # Render כבר מפנה לפורט הזה, אז נשתמש בו
    app.run(host="0.0.0.0", port=10000)