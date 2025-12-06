from flask import Flask, request
import telegram
import os

# שליפת הטוקן מה־Environment של Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env var is not set")

bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# דף בית לבדיקה מהדפדפן
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200


# Webhook של טלגרם
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = telegram.Update.de_json(data, bot)

        if update.message:
            chat_id = update.message.chat.id
            text = update.message.text or ""

            # כאן אפשר לשים לוגיקה של מעיין / פינג וכו'
            reply = f"הודעה התקבלה: {text}"
            bot.send_message(chat_id=chat_id, text=reply)

    except Exception as e:
        # חשוב: לא להפיל את השרת – רק להדפיס שגיאה ללוגים
        print("ERROR in /webhook:", e)

    # תמיד מחזירים 200 כדי שטלגרם לא ינתק את ה־webhook
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)