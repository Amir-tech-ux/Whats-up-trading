import os
import logging
from flask import Flask, request, jsonify
import requests

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

# ----- Flask app -----
app = Flask(__name__)


def send_message(chat_id: int, text: str) -> None:
    """שליחת הודעה לטלגרם"""
    try:
        resp = requests.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logging.error(
                "Failed to send message: %s - %s",
                resp.status_code,
                resp.text,
            )
    except Exception as e:
        logging.exception(f"Error sending message: {e}")


@app.route("/", methods=["GET"])
def index():
    """בריאות שירות פשוטה לרנדר"""
    return "Amir Trading Bot is running", 200


# --------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if not chat_id:
        return jsonify({"status": "no chat id"}), 200

    normalized = text.strip().lower()

    # ----- פקודות בסיס -----
    if normalized in ("/start", "start", "/start@amir_trading_bot"):
        reply = (
            "היי אמיר! ✅ הבוט מחובר ומוכן.\n\n"
            "פקודות זמינות:\n"
            "• /ping – בדיקת חיבור\n"
            "• שלח הודעת מסחר (לונג/שורט) – ואני אחזיר לך אישור שקיבלתי.\n\n"
            "נפתח בהדרגה טריגרים חכמים של 'מעיין'."
        )

    elif normalized in ("/ping", "ping", "/ping@amir_trading_bot"):
        reply = "pong ✅ הבוט חי ומחובר 🙂"

    else:
        # כאן בעתיד נוסיף פירוק חוקים של מעיין
        reply = (
            f"קיבלתי ממך:\n{text}\n\n"
            "✅ ההודעה הגיעה לשרת ברנדר.\n"
            "בהמשך נהפוך את זה לטריגר מסחר חכם."
        )

    # שליחת תשובה לטלגרם
    send_message(chat_id, reply)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)