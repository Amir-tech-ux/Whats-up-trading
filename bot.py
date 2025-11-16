import os
import logging
import re

from flask import Flask, request, jsonify
import requests

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)

# ---------- Telegram token ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ---------- Flask app ----------
app = Flask(__name__)


def send_message(chat_id: int, text: str) -> None:
    """Send a plain text message to Telegram and log the result."""
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        resp = requests.post(url, json=payload, timeout=5)
        logging.info(
            "Telegram sendMessage status=%s body=%s",
            resp.status_code,
            resp.text,
        )
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    # קח הודעה רגילה או הודעה ערוכה
    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not chat_id:
        return jsonify({"status": "no chat id"}), 200

    text = message.get("text", "") or ""
    lower = text.strip().lower()

    # ---------- Commands ----------
    if lower.startswith("/start"):
        send_message(
            chat_id,
            "הבוט פעיל! ✅\n"
            "שלח לי:\n"
            "• /ping או 'בדיקה'\n"
            "• אות מסחר למשל: 'לונג דאקס 01800 סטופ 17950'",
        )
        return jsonify({"status": "ok"}), 200

    if "ping" in lower or "פינג" in lower or "בדיקה" in lower:
        send_message(chat_id, "PONG ✅")
        return jsonify({"status": "ok"}), 200

    # ---------- Trading signal ----------
    # דוגמה: לונג דאקס 01800 סטופ 17950
    match = re.search(r"(לונג|שורט)\s+(\S+)\s+(\d+)\s+סטופ\s+(\d+)", text)
    if match:
        direction = match.group(1)     # לונג / שורט
        instrument = match.group(2)    # דאקס / נאסדק ...
        entry = match.group(3)         # 01800
        stop = match.group(4)          # 17950

        reply = (
            "📈 אות מסחר התקבל:\n"
            f"סוג: {direction}\n"
            f"נכס: {instrument}\n"
            f"כניסה: {entry}\n"
            f"סטופ: {stop}\n\n"
            "✅ נשמר. בהמשך נוסיף TP ופרוטוקול מעיין."
        )
        send_message(chat_id, reply)
        return jsonify({"status": "ok"}), 200

    # ברירת מחדל – לא זיהה כלום
    send_message(
        chat_id,
        "לא הבנתי ✋\n"
        "נסה /ping או דוגמה: 'לונג דאקס 01800 סטופ 17950'",
    )
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # להרצה מקומית (לא חובה ברנדר אבל לא מפריע)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)