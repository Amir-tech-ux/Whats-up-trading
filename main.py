from fastapi import FastAPI
import requests

app = FastAPI()

# הגדרות טלגרם
TELEGRAM_BOT_TOKEN = "8101329393:AAFnjuyu_f08n04G_2Rddl-WOaDYOg0U5a0"
CHAT_ID = 422909924

# פונקציה לשליחת הודעה
def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response.json()

# מסך בדיקה
@app.get("/")
def read_root():
    return {"message": "✅ WhatsApp Trading Bot is running!"}

# כתובת לבדיקה – שולחת הודעה
@app.get("/test")
def test():
    result = send_telegram_message("💬 הודעה נשלחה מהבוט בטסט!")
    return {"status": "sent", "result": result}
