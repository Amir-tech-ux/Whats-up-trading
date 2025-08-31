import os
import logging
import requests
from flask import Flask, request, jsonify

# ---------- Config & Setup ----------
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    logging.warning("TELEGRAM_TOKEN is missing from env vars!")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------- Helpers ----------
def send(chat_id: int, text: str):
    """שליחת הודעה לטלגרם"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        r = requests.post(url, json=payload, timeout=10)
        if not r.ok:
            logging.error("sendMessage failed: %s %s", r.status_code, r.text)
    except Exception as e:
        logging.exception("sendMessage exception: %
