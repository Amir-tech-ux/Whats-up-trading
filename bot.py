import os
from flask import Flask, request
import telebot

TOKEN = "הכנס_כאן_את_הטוקן_שלך"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # תופס גם application/json וגם application/json;charset=utf-8
    if "application/json" in request.headers.get("Content-Type", ""):
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Unsupported Media Type", 415


# ------------------------------
# Handlers
# ------------------------------
@bot.message_handler(commands=['ping'])
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "ping")
def ping_handler(message):
    bot.reply_to(message, "PONG ✅")


@bot.message_handler(func=lambda m: True)
def echo_handler(message):
    bot.reply_to(message, f"Received: {message.text}")


# ------------------------------
# Run Flask
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)