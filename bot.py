import os
import logging
import requests
from flask import Flask, request, jsonify

# ========= Config =========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://amir-trading-bot.onrender.com")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "amir404secret")

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TG_API = f"https://api.telegram.org/bot{TOKEN}"

# ========= App =========
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "🤖 הבוט של מעיין מחובר בהצלחה ל־Render ✅")
        else:
            send_message(chat_id, f"התקבל: {text}")

    return jsonify({"ok": True})

def send_message(chat_id, text):
    url = f"{TG_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))