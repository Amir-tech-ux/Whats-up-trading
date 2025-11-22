import os
import logging
import requests
from flask import Flask, request, jsonify

# ----- Telegram config -----
TELEGRAM_TOKEN = (
    os.environ.get("TELEGRAM_BOT_TOKEN")
    or os.environ.get("BOT_TOKEN")
)

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN / BOT_TOKEN is not set")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ----- Logging -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("amir-trading-bot")

# ----- Flask app -----
app = Flask(__name__)


def send_message(chat_id: int, text: str) -> None:
    """Send a text message to Telegram chat."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        # אם אתה רוצה תמיכה ב-HTML, אפשר להחזיר את השורה הבאה:
        # "parse_mode": "HTML",
    }

    try:
        resp = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        logger.info("Telegram sendMessage status=%s body=%s",
                    resp.status_code, resp.text[:300])
    except Exception as e:
        logger.exception("Error sending message to Telegram: %s", e)


@app.route("/", methods=["GET"])
def index():
    """Simple health-check."""
    return "Amir trading bot is running ✅", 200


@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Main Telegram webhook endpoint."""
    data = request.get_json(silent=True) or {}
    logger.info("Incoming update: %s", data)

    message = data.get("message") or data.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if not chat_id:
        return jsonify({"status": "no chat id"}), 200

    text = message.get("text") or ""
    normalized = text.strip().lower()

    # ----- basic commands -----
    if normalized in ("/start", "start", "/start@amir_trading_bot"):
        reply = (
            "היי אמיר! ✅ הבוט מחובר ל-Render ועובד.\n\n"
            "פקודות זמינות:\n"
            "• /ping – בדיקת חיבור\n"
            "• כל טקסט אחר – אחזיר 'קיבלתי' ואשר שההודעה עברה דרך השרת.\n"
        )
    elif normalized in ("/ping", "ping"):
        reply = "pong ✅ הבוט חי ומחובר."
    else:
        reply = (
            f"קיבלתי ממך:\n{text}\n\n"
            "✅ ההודעה הגיעה לשרת ברנדר וחזרה דרך הבוט."
        )

    send_message(chat_id, reply)
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)