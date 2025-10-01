import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== Telegram =====
TG_TOKEN = os.getenv("TG_TOKEN", os.getenv("TOKEN", ""))  # תומך גם בשם TOKEN הישן
TG_API = f"https://api.telegram.org/bot{TG_TOKEN}" if TG_TOKEN else ""

def tg_send(chat_id: str, text: str):
    if not TG_TOKEN:
        return {"ok": False, "error": "TG_TOKEN is missing"}
    r = requests.post(
        f"{TG_API}/sendMessage",
        data={"chat_id": chat_id, "text": text},
        timeout=10
    )
    return r.json()

@app.post("/tg/webhook")
def tg_webhook():
    if not TG_TOKEN:
        return jsonify({"ok": False, "error": "TG_TOKEN is missing"}), 400

    update = request.get_json(silent=True) or {}
    msg = update.get("message") or update.get("edited_message") or {}
    if not msg:
        return "ok", 200

    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()

    if not chat_id:
        return "ok", 200

    if text.lower() in ("/start", "start"):
        tg_send(chat_id, "מחובר לטלגרם ✅ הבוט פעיל")
    else:
        tg_send(chat_id, f"הודעה נקלטה: {text}")

    return "ok", 200


# ===== Facebook (Messenger / Page) =====
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")

def fb_send(psid: str, text: str):
    """שליחת הודעה ל־PSID דרך Graph API"""
    if not FB_PAGE_ACCESS_TOKEN:
        return {"ok": False, "error": "FB_PAGE_ACCESS_TOKEN is missing"}

    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": psid}, "message": {"text": text}}
    r = requests.post(url, params=params, json=payload, timeout=10)
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code, "text": r.text}

@app.get("/fb/webhook")
def fb_verify():
    """שלב אימות ה־Webhook בפייסבוק (GET)"""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if FB_VERIFY_TOKEN and token == FB_VERIFY_TOKEN:
        return challenge or "ok", 200
    return "Verification failed", 403

@app.post("/fb/webhook")
def fb_webhook():
    """קבלת הודעות מפייסבוק (POST)"""
    data = request.get_json(silent=True) or {}
    # אפשר להשאיר print ללוגים ב־Render
    print(json.dumps(data, ensure_ascii=False))

    for entry in data.get("entry", []):
        for evt in entry.get("messaging", []):
            sender = evt.get("sender", {}).get("id")
            msg = (evt.get("message") or {}).get("text")
            if sender and msg:
                # לוגיקה בסיסית: הֵד של ההודעה
                fb_send(sender, f"קיבלתי בפייסבוק: {msg}")

    return "ok", 200


# ===== Routes כלליים =====
@app.get("/")
def home():
    return "Trading Bot is running ✅"

@app.get("/whoami")
def whoami():
    return jsonify({
        "telegram": bool(TG_TOKEN),
        "facebook_page_access": bool(FB_PAGE_ACCESS_TOKEN)
    })


# ===== הרצה מקומית =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
