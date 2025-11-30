from flask import Flask, request
import telebot
import os

TOKEN = os.environ.get("BOT_TOKEN")
SECRET = os.environ.get("WEBHOOK_SECRET")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
        return "Unauthorized", 401

    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot is connected ✔️")


@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "PONG 🔥")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)