

import os
import json
import requests
from flask import Flask, request, jsonify
import logging

# ---- הגדרת לוגים ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---- יצירת אפליקציית Flask ----
app = Flask(__name__)

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)

    
if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)

# ===== Telegram =====
TG_TOKEN = os.getenv("TG_TOKEN") or os.getenv("TOKEN") or ""
TG_API   = f"https://api.telegram.org/bot{TG_TOKEN}" if TG_TOKEN else ""

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

    # ---- לוגים כדי לראות שהעדכון מגיע ----
    update = request.get_json(silent=True) or {}
    print("📩 Incoming update:", json.dumps(update, ensure_ascii=False))

    msg = update.get("message") or update.get("edited_message") or {}
    if not msg:
        return "ok", 200

    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()
    print(f"➡️ Got text: '{text}' from chat_id: {chat_id}")

    if not chat_id:
        return "ok", 200

    if text.lower() in ("/start", "start"):
        tg_send(chat_id, "מחובר לטלגרם ✅ הבוט פעיל")
    else:
        tg_send(chat_id, f"הודעה נקלטה: {text}")

    return "ok", 200


# ===== Facebook (Messenger/Page) — אופציונלי, אפשר להשאיר לעתיד =====
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")

def fb_send(psid: str, text: str):
    """שליחת הודעה ל-PSID דרך Graph API"""
    if not FB_PAGE_ACCESS_TOKEN:
        return {"ok": False, "error": "FB_PAGE_ACCESS_TOKEN is missing"}

    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": psid}, "message": {"text": text}}

    try:
        r = requests.post(url, params=params, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "text": str(e)}

@app.get("/fb/webhook")
def fb_verify():
    """אימות Webhook (GET)"""
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if FB_VERIFY_TOKEN and token == FB_VERIFY_TOKEN:
        return challenge or "ok", 200
    return "verification failed", 403

@app.post("/fb/webhook")
def fb_webhook():
    """קליטת התראות (POST)"""
    data = request.get_json(silent=True) or {}
    print("📨 FB Webhook:", json.dumps(data, ensure_ascii=False))
    for entry in data.get("entry", []):
        for evt in entry.get("messaging", []):
            sender = evt.get("sender", {}).get("id")
            msg = (evt.get("message") or {}).get("text")
            if sender and msg:
                fb_send(sender, f"קיבלתי: {msg}")
    return "ok", 200


# ===== עמודי בדיקה קטנים =====
@app.get("/")
def home():
    return "Maayan bot is running ✅"

@app.get("/whoami")
def whoami():
    return jsonify({"env": {
        "TG_TOKEN": bool(TG_TOKEN),
        "FB_VERIFY_TOKEN": bool(FB_VERIFY_TOKEN),
        "FB_PAGE_ACCESS_TOKEN": bool(FB_PAGE_ACCESS_TOKEN),
    }})
logging.INFO)

# ---- helper function ----
def send_message(chat_id: int, text: str):
    try:
        r = requests.post(
            f"{TG_API}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        if r.status_code != 200:
            app.logger.error("sendMessage failed: %s %s", r.status_code, r.text)
    except Exception as e:
        app.logger.error("sendMessage error: %s", e)


# ========= Routes =========
@app.route("/", methods=["GET"])
def health():
    """בדיקת תקינות"""
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """קליטת הודעות מטלגרם"""
    if request.args.get("secret") != WEBHOOK_SECRET:
        return "forbidden", 403

    try:
        update = request.get_json(force=True)
        app.logger.info(update)

        if not update or "message" not in update:
            return jsonify(ok=True)

        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text.startswith("/start"):
    send_message(chat_id, "✅ מחובר בהצלחה Amir_Trading_Bot!\nהקלדה /")

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 10000))
    serve(app, host="0.0.0.0", port=port)