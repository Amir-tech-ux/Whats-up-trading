@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    low = text.lower()

    if low.startswith("/start"):
        send(chat_id, "👋 הבוט מחובר דרך Render ועובד בהצלחה!")
    elif low.startswith("/status"):
        send(chat_id, "✅ פעיל | Webhook OK")
    elif low.startswith("/ping"):
        send(chat_id, "🏓 pong")
    elif low.startswith("/help"):
        send(chat_id, "📖 פקודות:\n/start - התחלה\n/status - בדיקה\n/ping - בדיקה\n/push <טקסט> - שליחת פוש\n/signal - אות מסחר")
    elif low.startswith("/push"):
        payload = text[5:].strip() or "הודעה ריקה"
        send(chat_id, f"📢 PUSH: {payload}")
    elif low.startswith("/signal"):
        send(chat_id, "📊 אות מסחר (דוגמה) 🚀")
    else:
        send(chat
