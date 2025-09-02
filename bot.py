import os
from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")  # אל תכתוב טוקן בקוד! שים ב-Render
# דוגמה ב-Render: RECIPIENT_IDS="123456789,987654321"
RECIPIENT_IDS = [int(x) for x in os.getenv("RECIPIENT_IDS", "").replace(" ", "").split(",") if x]

def send_to_all(context, text):
    for cid in RECIPIENT_IDS:
        try:
            context.bot.send_message(chat_id=cid, text=text, disable_web_page_preview=True)
        except Exception as e:
            # ממשיכים גם אם נכשלה שליחה לאחד מהם
            pass

def start(update, context):
    update.message.reply_text("✅ הבוט פעיל! /whoami יציג את ה-Chat ID שלך.\n/use: /alert, /signal")
def status(update, context):
    update.message.reply_text("📡 סטטוס: פעיל | Polling OK")
def ping(update, context):
    update.message.reply_text("🏓 pong")

# מציג את ה-Chat ID של השולח (כדי שתאסוף לשני המכשירים)
def whoami(update, context):
    cid = update.effective_chat.id
    update.message.reply_text(f"🆔 Chat ID: {cid}")

# התראה בסיסית -> לשני המכשירים
def alert(update, context):
    text = "🚨 התראה בסיסית – בדיקת שידור כפול"
    send_to_all(context, text)
    update.message.reply_text("✅ נשלח לשני המכשירים.")

# איתות מסחר “חי” (פשוט – פרמטרים מהפקודה)
# שימוש: /signal_live USDJPY short 148.60 148.90 147.80
def signal_live(update, context):
    try:
        symbol, direction, entry, sl, tp = context.args
        msg = (
            f"📊 אות חי\n"
            f"נכס: {symbol}\n"
            f"כיוון: {direction.upper()}\n"
            f"כניסה: {entry}\n"
            f"סטופ: {sl}\n"
            f"יעד: {tp}"
        )
        send_to_all(context, msg)
        update.message.reply_text("✅ האות נשלח לשני המכשירים.")
    except ValueError:
        update.message.reply_text("שימוש: /signal_live <symbol> <long/short> <entry> <sl> <tp>")

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN חסר כמשתנה סביבה")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("whoami", whoami))
    dp.add_handler(CommandHandler("alert", alert))
    dp.add_handler(CommandHandler("signal_live", signal_live))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
