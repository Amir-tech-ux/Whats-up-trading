import os
import re
import logging
from flask import Flask, request, jsonify
import requests

# ---------- App ----------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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


# ---------- Helper: trading trigger analyzer ----------
def analyze_trading_trigger(text: str) -> str | None:
    """
    מקבל טקסט חופשי מהטלגרם ומנסה להבין:
    - כיוון (לונג / שורט)
    - נכס (דאקס, נאסד״ק, דולר/ין וכו')
    - רמות מחיר שהוזכרו
    מחזיר טקסט תשובה, או None אם לא זיהינו כלום.
    """
    lower = text.lower()

    # כיוון
    direction = None
    if any(word in lower for word in ["long", " לונג", "לונג "]):
        direction = "LONG 📈 (לונג)"
    elif any(word in lower for word in ["short", " שורט", "שורט "]):
        direction = "SHORT 📉 (שורט)"

    # נכס
    instrument = None
    instruments = [
        (["dax", "ger40", "דקס"], "GER40 / DAX"),
        (["nas", "nasdaq", "נאסדק"], "NASDAQ"),
        (["usd/jpy", "דולר/ין", "דולר ין", "usdjpy"], "USD/JPY"),
        (["eur/usd", "יורו דולר", "eurusd"], "EUR/USD"),
        (["gold", "xau", "זהב"], "GOLD"),
        (["oil", "brent", "נפט"], "OIL"),
    ]
    for keys, name in instruments:
        if any(k in lower for k in keys):
            instrument = name
            break

    # רמות מספריות (מחירים, סטופים, טייקים)
    # דוגמה: 154.70, 18000, 1.0652 וכו'
    levels = re.findall(r"\d+(?:\.\d+)?", text)

    if not direction and not instrument and not levels:
        return None

    lines = ["🔍 זיהיתי טריגר מסחר מההודעה שלך:"]
    if direction:
        lines.append(f"• כיוון: {direction}")
    if instrument:
        lines.append(f"• נכס: {instrument}")
    if levels:
        pretty = ", ".join(levels)
        lines.append(f"• רמות מספריות שהוזכרו: {pretty}")
        if len(levels) >= 2:
            lines.append("  (תוכל לכתוב מפורש: כניסה / סטופ / טייק, כדי שאבין יותר טוב)")

    lines.append("")
    lines.append("⚠ זהו ניתוח טכסטואלי בלבד – לא הוראה לבצע פעולה.")
    lines.append("אם תרצה, תכתוב לי בצורה ברורה למשל:")
    lines.append("״שורט דאקס 18000 סטופ 18120 טייק 17750״")

    return "\n".join(lines)


# ---------- Webhook endpoint ----------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming update: {data}")

    if not data:
        return jsonify({"status": "no data"}), 200

    # קח את ההודעה הרלוונטית (חדשה או ערוכה)
    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"status": "no message"}), 200

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if chat_id is None:
        return jsonify({"status": "no chat id"}), 200

    text = message.get("text", "") or ""
    has_photo = "photo" in message

    lower = text.strip().lower()

    # ----- Commands -----
    if lower == "/start" or lower == "start":
        send_message(
            chat_id,
            "הבוט פעיל! ✅\n"
            "שלח /ping לבדיקה.\n\n"
            "אפשר לשלוח לי טריגר מסחר למשל:\n"
            "״שורט דאקס 18000 סטופ 18120״ או ״לונג דולר/ין 153.70״."
        )

    elif lower.startswith("/ping"):
        send_message(chat_id, "PONG ✅")

    else:
        # ניתוח טריגר למסחר מתוך הטקסט
        response_text = None
        if text:
            trigger_info = analyze_trading_trigger(text)
            if trigger_info:
                response_text = trigger_info

        # טיפול בתמונה
        if has_photo:
            if response_text:
                response_text += "\n\n📸 בנוסף קיבלתי את התמונה שצירפת."
            else:
                response_text = (
                    "📸 קיבלתי את התמונה.\n"
                    "אם תוסיף בטקסט כיוון (לונג/שורט), נכס ומחירים – אוכל לנתח את הטריגר."
                )

        # אם אין ניתוח מיוחד – אקו בסיסי
        if not response_text:
            if text:
                response_text = f"קיבלתי: {text}"
            else:
                response_text = "קיבלתי את ההודעה שלך ✅ (כרגע אין מה לנתח בה)."

        send_message(chat_id, response_text)

    # תשובה מהירה ל-Telegram שהכול תקין
    return jsonify({"status": "ok"}), 200


# ---------- Home page ----------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅", 200


# ---------- Local run (not used on Render) ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)