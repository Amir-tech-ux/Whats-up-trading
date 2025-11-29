import os
import logging
import requests
from flask import Flask, request, jsonify

# ----- Flask app -----
app = Flask(__name__)

# ----- Telegram config -----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ----- Logging -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def send_message(chat_id: int, text: str) -> None:
    """Send a message to a Telegram chat."""
    if not chat_id or not text:
        return
    try:
        payload = {"chat_id": chat_id, "text": text}
        resp = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload, timeout=10)
        if not resp.ok:
            logging.error("Failed to send message: %s", resp.text)
    except Exception as e:
        logging.exception("Error sending message: %s", e)


# ----- Health check -----
@app.route("/", methods=["GET"])
def index():
    return "Amir trading bot is alive ✅", 200


# ----- Telegram webhook endpoint -----
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or data.get("edited_message") or {}

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id:
        return jsonify({"ok": True}), 200

    normalized = text.lower() if text else ""

    # פקודת בדיקה /ping
    if normalized in ("/ping", "ping", "ping/"):
        reply = "pong ✅ הבוט חי ומחובר לרנדר."
    else:
        # בהמשך נוסיף כאן את חוקי 'מעיין' והאנליזה למסחר
        reply = f"קיבלתי ממך:\n{text}\nההודעה נקלטה בשרת Render ✅"

    send_message(chat_id, reply)
    return jsonify({"ok": True}), 200


# ----- Local run (לבדיקה מקומית, Render מתעלם מזה) -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)