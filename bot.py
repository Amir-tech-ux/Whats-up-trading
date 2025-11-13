import requests
from flask import Flask, request

# --- CONFIG ---
TOKEN = "8101329393:AAE36Q5txkc6HkdFikK_FfvvCsR_ocaKNro"
CHAT_ID = 422909924  # Amir

# --- FLASK APP ---
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    # אם מגיעה הודעה מהטלגרם
    if "message" in data:
        text = data["message"].get("text", "")
        send_message(f"הודעה התקבלה: {text}")

    return "OK", 200

def send_message(text):
    """שליחת הודעה חזרה לטלגרם"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

@app.route("/")
def home():
    return "Bot is running", 200

if __name__ == "__main__":
    app.run()