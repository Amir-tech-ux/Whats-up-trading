from flask import Flask, request
import os
import telegram

# טוקן מה־Environment של Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env var is not set")

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)


# דף בית לבדיקה מהדפדפן
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200


# Webhook של טלגרם
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)

        if not data:
            return "no data", 200

        # מוציאים message ו-chat_id ו-text
        message = data.get("message", {}) or {}
        chat = message.get("chat", {}) or {}
        chat_id = chat.get("id")
        text = (message.get("text") or "").strip()

        if not chat_id:
            return "no chat_id", 200

        if not text:
            # אין טקסט – לא עונים
            return "ok", 200

        # Ping -> PONG
        if text.lower() == "ping":
            bot.send_message(chat_id, "PONG ✅")
            return "ok", 200

        # פקודת בדיקה
        if text == "/test_alert":
            bot.send_message(
                chat_id,
                "🚨 Maayan Test Alert 🚨\nהתראת בדיקה מ-Render."
            )
            return "ok", 200

        # ברירת מחדל – סתם אישור שקיבלנו
        bot.send_message(chat_id, "✅ קיבלתי את ההודעה שלך.")
        return "ok", 200

    except Exception as e:
        print("Webhook error:", e)
        return "error", 200