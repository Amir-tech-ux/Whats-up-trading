@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)

        if not data:
            return "no data", 200

        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        # אם אין טקסט - זה עדכון מסוג אחר
        if not text:
            return "ok", 200

        # Ping → PONG
        if text.lower() == "ping":
            bot.send_message(chat_id, "PONG ✅")
            return "ok", 200

        # פקודת בדיקה
        if text == "/test_alert":
            bot.send_message(chat_id, "🚨 Maayan Test Alert 🚨\nהתראת בדיקה מרנדר.")
            return "ok", 200

        # ברירת מחדל
        bot.send_message(chat_id, "קיבלתי את ההודעה ✔️")
        return "ok", 200

    except Exception as e:
        print("Webhook error:", e)
        return "error", 200