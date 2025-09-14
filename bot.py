# bot.py
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ["TELEGRAM_TOKEN"]
SECRET = os.environ["WEBHOOK_SECRET"]
API = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id: int, text: str):
    try:
        requests.get(f"{API}/sendMessage", params={"chat_id": chat_id, "text": text})
    except Exception as e:
        print("send_message error:", e)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post(f"/webhook/{SECRET}")
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    print("UPDATE:", update)

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return jsonify(ok=True)

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    text = msg.get("text", "") or ""

    if not chat_id:
        return jsonify(ok=True)

    t = text.strip()

    # פקודות
    if t.startswith("/start"):
        send_message(chat_id, "🤖 ברוך הבא! הבוט מחובר ✅\nשלח לי טקסט ואני אחזור אליך.\nנסה /help כדי לראות פקודות.")
    elif t.startswith("/whoami"):
        name = chat.get("title") or chat.get("username") or chat.get("first_name", "לא ידוע")
        send_message(chat_id, f"אתה/ח: {name} (chat_id={chat_id})")
    elif t.startswith("/ping"):
        send_message(chat_id, "pong ✅")
    elif t.startswith("/help"):
        commands = (
            "📋 רשימת פקודות:\n"
            "/start – בדיקה ראשונית\n"
            "/whoami – להחזיר את השם שלך\n"
            "/ping – בדיקת חיים (pong)\n"
            "/help – רשימת פקודות\n"
            "✉️ כל טקסט אחר – אני אחזיר לך 'קיבלתי ✅'"
        )
        send_message(chat_id, commands)
    else:
        # כל טקסט אחר
        send_message(chat_id, f"קיבלתי ✅: {text}")

    return jsonify(ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
