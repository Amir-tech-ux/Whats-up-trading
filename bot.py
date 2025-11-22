import os
import logging
import requests
from flask import Flask, request, jsonify

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
    """Send a message to a Telegram chat and log the response."""
    resp = requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    logging.info("sendMessage status=%s body=%s", resp.status_code, resp.text)

@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    logging.info("Incoming update: %s", data)

    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"ok": True, "status": "no message"}), 200

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()
    normalized = text.lower()

    if not chat_id:
        return jsonify({"ok": True, "status": "no chat id"}), 200

    # ----- פקודות בסיס -----
    if normalized in ("/start", "/start@amir_trading_bot"):
        reply = (
            "היי אמיר! ✅ הבוט מחובר ומוכן.\n"
            "פקודות זמינות:\n"
            " • /ping – בדיקת חיבור\n"
            " • כל טקסט אחר – אני אחזור על מה שכתבת.\n"
        )
    elif normalized in ("/ping", "ping", "ping/"):
        reply = "pong ✅ הבוט חי ומחובר."
    else:
        reply = f"קיבלתי ממך:\n{text}\n\nההודעה הגיעה לשרת ברנדר ✅"

    send_message(chat_id, reply)
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)