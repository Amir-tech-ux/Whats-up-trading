from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# נתוני התחברות בסיסיים
TG_API = os.environ.get("TG_API")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
PUBLIC_URL = os.environ.get("PUBLIC_URL")

# בדיקת בריאות השרת
@app.route("/health")
def health():
    return jsonify({"status": "running"})

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
        update = request.get_json(force=True)
        print("Received update:", update)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))