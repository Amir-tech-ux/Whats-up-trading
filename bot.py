import os
import logging
import requests
from flask import Flask, request, jsonify

# ======== Config ========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PUBLIC_URL = "https://amir-trading-bot.onrender.com"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "amir404secret")

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TG_API = f"https://api.telegram.org/bot{TOKEN}"

# ======== App ========
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(update)

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        # שלח תשובה אוטומטית לטלגרם
        reply = {"chat_id": chat_id, "text": f"התקבל: {text}"}
        requests.post(f"{TG_API}/sendMessage", json=reply)

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))