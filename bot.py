import os
import httpx
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

TOKEN = os.environ["TELEGRAM_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "mysecret")

# נמעני פוש
PRIMARY_CHAT_ID = os.environ.get("PRIMARY_CHAT_ID", "")
SECONDARY_CHAT_ID = os.environ.get("SECONDARY_CHAT_ID_404", "")

async def tg_send(chat_id: str, text: str):
    if not chat_id:
        return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(f"{API}/sendMessage", data={"chat_id": chat_id, "text": text})

async def send_alert(text: str):
    await tg_send(PRIMARY_CHAT_ID, text)
    await tg_send(SECONDARY_CHAT_ID, text)

@app.on_event("startup")
async def on_startup():
    base = os.environ.get("RENDER_EXTERNAL_URL")
    if base:
        url = f"{base}/webhook/{WEBHOOK_SECRET}"
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{API}/setWebhook", data={"url": url})

@app.post("/webhook/{secret}")
async def webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")

    update = await request.json()
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = str(msg["chat"]["id"])
    text = (msg.get("text") or "").strip()

    # פקודות
    if text.lower() in ("/start", "start", "/start/", "/Start", "/Start/"):
        await tg_send(chat_id, "✅ הבוט פעיל. פקודות: /ping, /whoami, /broadcast <טקסט>")

    elif text.lower() == "/ping":
        await tg_send(chat_id, "🏓 pong")

    elif text.lower() == "/whoami":
        await tg_send(chat_id, f"ℹ️ chat_id שלך: {chat_id}")

    elif text.lower().startswith("/broadcast "):
        admin_id = os.environ.get("PRIMARY_CHAT_ID", "")
        if admin_id and chat_id == admin_id:
            payload = text[len("/broadcast "):].strip()
            await send_alert(f"📢 {payload}")
            await tg_send(chat_id, "✅ נשלח לשני המכשירים")
        else:
            await tg_send(chat_id, "⛔ הפקודה זמינה רק לאדמין")

    return {"ok": True}

@app.get("/")
def root():
    return {"ok": True}
