from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

# -----------------------------
#  ROUTES
# -----------------------------

@app.route("/", methods=["GET"])
def home():
    return "Bot is running", 200


@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    # Check secret token in URL
    if secret != WEBHOOK_SECRET:
        return Response("forbidden", status=403)

    # Check secret header from Telegram
    secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if secret_header != WEBHOOK_SECRET:
        return Response("forbidden", status=403)

    update = request.get_json(silent=True)
    print("Incoming update:", update)

    if not update:
        return Response("no update", status=200)

    # Handle message
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text.lower() in ["/start", "start"]:
            send_message(chat_id, "הבוט מחובר ועובד ✔️")
        elif text.lower() == "/ping":
            send_message(chat_id, "Pong ✔️")
        else:
            send_message(chat_id, f"קיבלתי: {text}")

    return Response("ok", status=200)


# -----------------------------
#  SEND MESSAGE TO TELEGRAM
# -----------------------------

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# -----------------------------
#  RUN (for local debug)
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)