import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- ENV (ב-Render) ---
TOKEN = os.getenv("TOKEN")           # הטוקן מ-BotFather
API = f"https://api.telegram.org/bot{TOKEN}/"

# --- Helpers ---
def send_text(chat_id: str, text: str):
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    try:
        r = requests.post(API + "sendMessage",
                          data={"chat_id": chat_id, "text": text},
                          timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def updates():
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    return requests.get(API + "getUpdates", timeout=10).json()

def find_chat_ids():
    js = updates()
    found, seen = [], set()
    for u in js.get("result", []):
        msg = u.get("message") or u.get("edited_message") \
              or (u.get("callback_query", {}).get("message") if u.get("callback_query") else None)
        if not msg:
            continue
        chat = msg.get("chat", {})
        cid = chat.get("id")
        if cid and cid not in seen:
            seen.add(cid)
            found.append({
                "chat_id": cid,
                "first_name": chat.get("first_name"),
                "username": chat.get("username"),
                "title": chat.get("title"),
            })
    return found

# --- Routes ---
@app.get("/")
def home():
    return "Maayan bot is running ✅"

@app.get("/whomai")
def whomai():
    """הדפסה מהירה של Chat IDs שנמצאו דרך getUpdates"""
    return jsonify({"found": find_chat_ids()})

# === Webhook endpoint for Telegram ===
@app.post("/webhook")
def webhook():
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}, 400

    update = request.get_json(silent=True) or {}

    # הודעת טקסט רגילה
    msg = update.get("message") or update.get("edited_message")
    if msg and "text" in msg:
        chat_id = msg["chat"]["id"]
        text = msg["text"].strip()

        if text.lower() in ("/start", "start"):
            send_text(chat_id, "הבוט מחובר! ✅ שלח הודעה לבדיקת אקו.")
        else:
            send_text(chat_id, f"אתה כתבת: {text}")
        return {"ok": True}, 200

    # Callback של כפתורים
    cq = update.get("callback_query")
    if cq:
        chat_id = cq["message"]["chat"]["id"]
        data = cq.get("data", "")
        send_text(chat_id, f"נלחץ: {data}")
        return {"ok": True}, 200

    return {"ok": True}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
