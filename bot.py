import os
import logging
import requests
from flask import Flask, request, jsonify

# ======= Config =======
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://amir-trading-bot.onrender.com")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "amir404secret")
TG_API = f"https://api.telegram.org/bot{TOKEN}"
MT_SECRET = os.environ.get("MT_SECRET", "change_me")  # למטא-טריידר

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")
if not PUBLIC_URL:
    raise RuntimeError("Missing PUBLIC_URL env var (e.g. https://<app>.onrender.com)")

# ======= App =======
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# הגדרת webhook מול טלגרם
@app.route("/set_webhook")
def set_webhook():
    url = f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"
    r = requests.post(f"{TG_API}/setWebhook", json={"url": url}, timeout=10)
    ok = r.json().get("ok", False)
    return jsonify({"ok": ok, "url": url, "resp": r.json()}), (200 if ok else 500)

# נקודת קליטת עדכונים מטלגרם
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        update = request.get_json(force