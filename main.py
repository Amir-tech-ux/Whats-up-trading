import logging
from flask import Flask, request
import requests

TOKEN = "8101329393:AAFmph9j-_mMV5PrOLoJnqDws4J7G78lKLU"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() in ["/ping", "ping", "/ping/"]:
            send_message(chat_id, "PONG ✔️")
        elif text.lower() == "/start":
            send_message(chat_id, "הבוט פעיל ועובד! ✔️")
        else:
            send_message(chat_id, f"קיבלתי: {text}")

    return "OK"


def send_message(chat_id, text):
    requests.post(URL, json={"chat_id": chat_id, "text": text})


@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)