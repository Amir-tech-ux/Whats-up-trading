import os
from flask import Flask, request
import telebot

# === Environment variables from Render ===
TOKEN = os.environ.get("TELEGRAM_TOKEN")      # הטוקן מה-BotFather
SECRET = os.environ.get("WEBHOOK_SECRET", "") # למשל: amir404secret

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set in environment variables")

# === Telegram bot ===
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# === Flask app ===
app = Flask(__name__)


# בריאות / בדיקה - Render יכול לקרוא ל-root
@app.route("/", methods=["GET"])
def index():
    return "Amir Trading Bot is running ✅", 200


# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    # בדיקת הסיקרט מה-Header של טלגרם
    if SECRET:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != SECRET:
            return "Unauthorized", 401

    # קבלת ה-JSON מהבקשה
    json_data = request.get_data().decode("utf-8")

    # המרה ל-Update של telebot
    update = telebot.types.Update.de_json(json_data)

    # עיבוד ההודעה ע"י הבוט
    bot.process_new_updates([update])

    return "OK", 200


# === Handlers ===

@bot.message_handler(commands=["start"])
def handle_start(message):
    text = (
        "👋 שלום אמיר!\n"
        "Amir_Trading_Bot מחובר ועובד.\n\n"
        "תכתוב /ping כדי לבדוק חיבור 🙂"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["ping"])
def handle_ping(message):
    bot.reply_to(message, "pong ✅")


# ברירת מחדל – מחזיר כל טקסט
@bot.message_handler(content_types=["text"])
def handle_text(message):
    reply = f"🤖 קיבלתי: {message.text}"
    bot.reply_to(message, reply)


# === Run Flask app on Render ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    # Render צריך שהאפליקציה תאזין על 0.0.0.0 וב-port מה-ENV
    app.run(host="0.0.0.0", port=port)