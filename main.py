from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

# לוקחים את הטוקן כמו שהוא מוגדר ב-Render: BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # שולחים חזרה אקו לטלגרם
        requests.post(
            TELEGRAM_URL,
            json={
                "chat_id": chat_id,
                "text": f"Echo: {text}",
            }
        )

    return {"ok": True}