from flask import Flask, request
import os
import telegram

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telegram.Bot(token=TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if not data:
        return "no data", 200

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return "no chat", 200

    if text.lower() == "ping":
        bot.send_message(chat_id, "PONG ✅")
        return "ok", 200

    bot.send_message(chat_id, f"Received: {text}")
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
