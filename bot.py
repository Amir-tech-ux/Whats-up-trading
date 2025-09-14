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
        requests.get(f"{API}/sendMessage", params={"chat_id": chat_id, "text": text}, timeout=7)
    except Exception as e:
        print("send_message error:", e)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post(f"/webhook/{SECRET}")
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    print("UPDATE:", update)  # תראה את זה ב-Render Logs

    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return jsonify(ok=True)  # לא הודעת צ׳אט רגילה (callback/query וכו')

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    text = msg.get("text", "") or ""

    if not chat_id:
        return jsonify(ok=True)

    # ---- פקודות בסיס ----
    t = text.strip()

    if t.startswith("/start"):
        send_message(chat_id, "היי! הבוט מחובר ✅ שלח לי טקסט ואני אחזיר אותו אליך.")
    elif t.startswith("/whoami"):
        name = chat.get("title") or chat.get("username") or chat.get("first_name") or "unknown"
        send_message(chat_id, f"את/ה: {name} (chat_id={chat_id})")
    elif t.startswith("/ping"):
        send_message(chat_id, "pong ✅")
    else:
        # ברירת מחדל: אקו
        send_message(chat_id, f"✅ קיבלתי: {text}")

    return jsonify(ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
