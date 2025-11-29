import os
import logging
import requests
from flask import Flask, request, jsonify, Response

# ---------- Telegram config ----------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    # אם הטוקן לא מוגדר ברנדר – נעצור את האפליקציה עם שגיאה ברורה
    raise RuntimeError("TELEGRAM_TOKEN env var is missing")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# אם אתה רוצה להשתמש בסיקרט מה-Environment (לא חובה)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------- Flask app ----------
app = Flask(__name__)


def send_message(chat_id: int, text: str) -> None:
    """
    שולח הודעה לצ'אט בטלגרם
    """
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        resp = requests.post(
            TELEGRAM_API_URL + "sendMessage",
            json=payload,
            timeout=5,
        )
        if resp.status_code != 200:
            logging.error("send_message failed: %s - %s", resp.status_code, resp.text)
    except Exception as e:
        logging.exception("Exception in send_message: %s", e)


# ---------- Routes ----------

@app.route("/", methods=["GET"])
def home():
    """
    בדיקת חיים – כשנכנסים מהדפדפן ל-/
    """
    return "Maayan trading bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Main Telegram webhook endpoint.
    """
    # בדיקת סיקרט (אם הגדרת)
    if WEBHOOK_SECRET:
        secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret_header != WEBHOOK_SECRET:
            logging.warning("Invalid webhook secret")
            return Response("forbidden", status=403)

    update = request.get_json(force=True, silent=True) or {}
    logging.info("Incoming update: %s", update)

    # מקבלים את ההודעה
    message = update.get("message") or update.get("edited_message")
    if not message:
        # אם זה לא הודעה רגילה (כמו callback), מתעלמים
        return jsonify({"ok": True})

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return jsonify({"ok": True})

    normalized = text.lower()

    # ----- Commands -----
    if normalized.startswith("/start"):
        reply = (
            "היי אמיר 👋\n"
            "הבוט של מעיין מחובר לרנדר ועובד ✅\n"
            "נסה לשלוח /ping לבדיקה."
        )

    elif normalized.startswith("/ping"):
        reply = "pong ✅ הבוט חי ומחובר לרנדר."

    else:
        # אקו פשוט לכל טקסט אחר
        reply = f"קיבלתי ממך:\n{text}\nההודעה הגיעה לשרת ברנדר ✅"

    # שולחים תשובה
    send_message(chat_id, reply)
    return jsonify({"ok": True})


# ---------- Local / Render run ----------
if __name__ == "__main__":
    # ברנדר PORT מגיע מה-Environment; מקומית – ברירת מחדל 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)