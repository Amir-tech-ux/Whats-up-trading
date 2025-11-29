import os
import logging
import requests
from flask import Flask, request, jsonify, Response

# -------- Telegram config --------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in environment variables")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# -------- Logging --------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)


def send_message(chat_id: int, text: str) -> None:
    """
    Send a message to a Telegram chat.
    """
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        resp = requests.post(TELEGRAM_API_URL + "sendMessage", json=payload, timeout=5)
        if resp.status_code != 200:
            logging.error("send_message failed: %s - %s", resp.status_code, resp.text)
    except Exception as e:
        logging.exception("Exception in send_message: %s", e)


# -------- Routes --------

@app.route("/", methods=["GET"])
def home():
    """
    Health-check route for browser / Render.
    """
    return "Maayan trading bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Main Telegram webhook endpoint.
    """
    update = request.get_json(force=True, silent=True)
    logging.info("Incoming update: %s", update)

    if not update:
        return Response("no update", status=400)

    message = update.get("message") or update.get("edited_message")
    if not message:
        # ignore non-message updates (callback_query וכו')
        return jsonify({"ok": True})

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return jsonify({"ok": True})

    normalized = text.lower()

    # ---- Commands ----
    if normalized.startswith("/start"):
        reply = (
            "היי אמיר 👋\n"
            "הבוט של מעיין מחובר לרנדר ועובד ✅\n"
            "נסה לשלוח /ping לבדיקה."
        )

    elif normalized.startswith("/ping"):
        reply = "pong ✅ הבוט חי ומחובר לרנדר."

    else:
        # כל טקסט אחר – אקו פשוט
        reply = f"קיבלתי ממך:\n{text}\nההודעה הגיעה לשרת ברנדר ✅"

    send_message(chat_id, reply)
    return jsonify({"ok": True})


# לא חובה ברנדר, אבל נוח להרצה מקומית
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)