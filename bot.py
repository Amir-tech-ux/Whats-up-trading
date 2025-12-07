import os
import json
from flask import Flask, request
import telebot

# *** IMPORTANT: put your real token here ***
TOKEN = "הכנס_כאן_את_הטוקן_שלך"

bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)


# Simple index for tests / health
@app.route("/", methods=["GET"])
def index():
    return "OK", 200


# Telegram webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    content_type = request.headers.get("Content-Type", "")

    if content_type.startswith("application/json"):
        json_str = request.get_data().decode("utf-8")
        data = json.loads(json_str)

        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])

        return "OK", 200

    # If content-type is not JSON
    return "Unsupported Media Type", 415


# ------------ Handlers ------------

@bot.message_handler(commands=["ping"])
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "ping")
def ping_handler(message):
    bot.reply_to(message, "PONG ✅")


@bot.message_handler(func=lambda m: True)
def echo_handler(message):
    bot.reply_to(message, f"Received: {message.text}")


# ------------ Run Flask (for local dev) ------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)