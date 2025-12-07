import os
from flask import Flask, request
import telebot

TOKEN = "YOUR_TOKEN"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(commands=['ping'])
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "ping")
def ping_handler(message):
    bot.reply_to(message, "PONG ✅")


@bot.message_handler(func=lambda m: True)
def echo_handler(message):
    bot.reply_to(message, f"Received: {message.text}")


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )