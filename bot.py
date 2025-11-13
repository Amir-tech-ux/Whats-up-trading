import telebot
from flask import Flask, request

API_TOKEN = "הכנס_כאן_את_הטוקן_שלך"   # הטוקן מבוטפאדר
CHAT_ID = 422909924                   # זה ה־Chat ID שלך

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- פונקציה לשליחת הודעות PUSH ---
def send_alert(message):
    bot.send_message(CHAT_ID, message)

# --- בדיקה שהבוט חי ---
@app.route("/", methods=['GET'])
def home():
    return "Bot is running", 200

# --- Webhook שקולט הודעות מטלגרם ---
@app.route("/webhook", methods=['POST'])
def webhook():
    json_data = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# --- תגובה לכל הודעה שאתה שולח לבוט ---
@bot.message_handler(func=lambda message: True)
def echo(message):
    send_alert("✔️ קיבלתי: " + message.text)

# --- הפעלת הבוט ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)