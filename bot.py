from flask import Flask, request
import telebot
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")  # ✔ משתמש במפתח הנכון
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Bot is running", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(commands=['ping', 'Ping'])
def ping(message):
    bot.reply_to(message, "PONG")


if __name__ == "__main__":
    bot.remove_webhook()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))