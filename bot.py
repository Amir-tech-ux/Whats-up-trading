# bot.py
import os
import requests
from flask import Flask, request, jsonify

# ====== Config (Render env) ======
TOKEN  = os.environ["TG_TOKEN"]            # ברנדר: TG_TOKEN
SECRET = os.environ.get("WEBHOOK_SECRET", "amir404secret")
API    = f"https://api.telegram.org/bot{TOKEN}"

# ====== App ======
app = Flask(__name__)

def send_message(chat_id: int, text: str):
    try:
        requests.get(f"{API}/sendMessage",
                     params={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("send_message error:", e)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post(f"/webhook/{SECRET}")
def telegram_webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message") or data.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()
    low = text.lower()

    if not chat_id:
        return jsonify(ok=True)

    if low.startswith("/start"):
        send_message(chat_id, "✅ הבוט מחובר ועובד")
    elif low.startswith("/ping"):
        send_message(chat_id, "pong ✅")
    elif low.startswith("/status"):
        try:
            r = requests.get("https://amir-trading-bot.onrender.com/health", timeout=5)
            if r.status_code == 200:
                send_message(chat_id, "🟢 שרת חי (status=ok)")
            else:
                send_message(chat_id, f"🔴 קוד מצב: {r.status_code}")
        except Exception as e:
            send_message(chat_id, f"⚠️ שגיאה בבדיקת סטטוס: {e}")
    else:
        send_message(chat_id, f"📩 קיבלתי: {text}")

    return jsonify(ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)