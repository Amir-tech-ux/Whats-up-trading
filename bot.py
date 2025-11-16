import os
import logging
import re
from flask import Flask, request, jsonify
import requests

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)

# ---------- App ----------
app = Flask(__name__)

# ---------- Telegram Token ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


# ---------- Helper: send message ----------
def send_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


# ---------- Trading signal parser ----------
def parse_trading_signal(text: str) -> str | None:
    """
    מנסה לזהות הודעת מסחר בסגנון:
    'לונג דאקס 01800 סטופ 17950'
    'שורט nasdaq 16000 סטופ 16100'
    ומחזיר טקסט תשובה יפה, או None אם לא זוהה.
    """

    lower = text.strip().lower()

    # צד העסקה
    side = None
    if "לונג" in text or "long" in lower:
        side = "לונג"
    elif "שורט" in text or "short" in lower:
        side = "שורט"

    if not side:
        return None

    # מנסים לזהות נכס (המילה אחרי לונג/שורט)
    asset = "לא צוין"
    words = text.split()
    for i, w in enumerate(words):
        if w in ("לונג", "long", "שורט", "short"):
            if i + 1 < len(words):
                asset = words[i + 1]
            break

    # מחירים (מספרים) – נניח ראשון = כניסה, שני = סטופ
    nums = re.findall(r"\d+", text)
    entry = nums[0] if len(nums) >= 1 else "לא צוין"
    stop = nums[1] if len(nums) >= 2 else "לא צוין"

    reply = (
        "📊 קיבלתי אות מסחר:\n"
        f"• צד: {side}\n"
        f"• נכס: {asset}\n"
        f"• כניסה: {entry}\n"
        f"• סטופ: {stop}\n\n"
        "⚠️ שים לב: זה רק אישור טכני של קבלת ההודעה, "
        "לא המלצה לביצוע עסקה."
    )
    return reply


# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    # לוקחים את ההודעה הרלוונטית (רגילה או ערוכה)
    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    # טיפול בתמונות
    if "photo" in message:
        # אפשר גם לקרוא caption אם יש
        caption = message.get("caption", "")
        reply = "📸 קיבלתי תמונה."
        if caption:
            reply += f"\nכיתוב: {caption}"
        if chat_id is not None:
            send_message(chat_id, reply)
        return jsonify({"status": "ok"}), 200

    # טקסט רגיל
    text = message.get("text", "")
    if chat_id is None or not text:
        return jsonify({"status": "ok"}), 200

    lower = text.strip().lower()

    # ----- Commands -----
    if lower.startswith("/start"):
        send_message(
            chat_id,
            "הבוט פעיל! ✅\n"
            "/ping או 'בדיקה' – לבדיקה.\n"
            "תוכל לשלוח גם אות מסחר, למשל:\n"
            "לונג דאקס 01800 סטופ 17950"
        )

    elif lower.startswith("/ping") or "בדיקה" in text:
        send_message(chat_id, "PONG ✅")

    else:
        # קודם ננסה לפרש כאות מסחר
        signal_reply = parse_trading_signal(text)
        if signal_reply:
            send_message(chat_id, signal_reply)
        else:
            # אקו רגיל
            send_message(chat_id, f"קיבלתי: {text}")

    # תשובת OK לטלגרם
    return jsonify({"status": "ok"}), 200


# ---------- Home page ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅", 200


# ---------- Local run (לא בשימוש ברנדר) ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)