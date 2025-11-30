from flask import Flask, request
import telegram
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# דף בית רק כדי לבדוק שהשרת חי
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

# ה־webhook של טלגרם
@app.route("/webhook", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    text = update.message.text

    bot.sendMessage(chat_id=chat_id, text=f"הודעה התקבלה: {text}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)