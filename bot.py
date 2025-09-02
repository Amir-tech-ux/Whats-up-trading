from telegram.ext import Updater, CommandHandler

# שים כאן את הטוקן שקיבלת מ-BotFather
TOKEN = "הכנס_כאן_את_הטוקן_שלך"

# פקודת /start
def start(update, context):
    update.message.reply_text("✅ הבוט פעיל ומחובר!")

# פקודת /status
def status(update, context):
    update.message.reply_text("📡 סטטוס: פעיל | Webhook OK")

# פקודת /ping
def ping(update, context):
    update.message.reply_text("🏓 pong")

# פקודת /alert
def alert(update, context):
    update.message.reply_text("🚨 התקבלה התראה בסיסית! 🚨")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # חיבור הפקודות
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("alert", alert))

    # הפעלת הבוט
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
