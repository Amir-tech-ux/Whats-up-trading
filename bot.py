import os
import time
import requests
import numpy as np
import pandas as pd
from telegram.ext import Updater, CommandHandler

PAIR = "USD/JPY"
SYMBOL_FROM = "USD"
SYMBOL_TO = "JPY"

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
if not ALPHA_KEY:
    raise RuntimeError("Missing ALPHA_VANTAGE_KEY env var")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN env var")

# -------- data --------
def get_fx_series(interval="60min", output_size="compact"):
    """
    interval: '60min' / '15min'
    returns pandas Series of closes (float) newest first
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=FX_INTRADAY&from_symbol={SYMBOL_FROM}&to_symbol={SYMBOL_TO}"
        f"&interval={interval}&outputsize={output_size}&apikey={ALPHA_KEY}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    key = f"Time Series FX ({interval})"
    if key not in data:
        raise RuntimeError(f"AlphaVantage error: {data.get('Note') or data.get('Error Message') or data}")
    df = pd.DataFrame.from_dict(data[key], orient="index").sort_index()
    closes = df["4. close"].astype(float)
    return closes

def rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=series.index).rolling(period).mean()
    roll_down = pd.Series(down, index=series.index).rolling(period).mean()
    rs = roll_up / (roll_down + 1e-12)
    rsi_val = 100.0 - (100.0 / (1.0 + rs))
    return float(rsi_val.iloc[-1])

def get_price():
    closes = get_fx_series("15min", "compact")
    return float(closes.iloc[-1])

# -------- logic --------
def plan_signal():
    """
    מחזיר טקסט איתות + רמות SL/TP על סמך RSI 15/60 דק' ורמת 149.00
    """
    closes_60 = get_fx_series("60min", "compact")
    closes_15 = get_fx_series("15min", "compact")
    price = float(closes_15.iloc[-1])

    rsi60 = rsi(closes_60, 14)
    rsi15 = rsi(closes_15, 14)

    resistance = 149.00
    support = 148.00

    msg_lines = [
        f"📈 *{PAIR}* — מחיר נוכחי: *{price:.3f}*",
        f"RSI(60min): *{rsi60:.1f}* | RSI(15min): *{rsi15:.1f}*",
        "—" * 15,
    ]

    idea = ""
    entry = None
    sl = None
    tp1 = None
    tp2 = None

    # כללים פשוטים:
    # 1) שורט: אם RSI60>=70 או RSI15>=75 ובמיוחד אם המחיר קרוב/מעל 149.00
    # 2) לונג: אם RSI60<=30 או RSI15<=25 ליד 148.00
    near_res = abs(price - resistance) <= 0.15
    near_sup = abs(price - support) <= 0.15

    if (rsi60 >= 70 or rsi15 >= 75) and (near_res or price >= resistance - 0.05):
        idea = "🔻 *תסריט שורט*"
        # כניסה עדינה קצת מתחת להתנגדות
        entry = max(price, resistance - 0.03)
        sl = resistance + 0.30  # כרית ~30 פיפס מעל 149.00
        tp1 = resistance - 0.50  # 148.50
        tp2 = resistance - 0.80  # 148.20
    elif (rsi60 <= 30 or rsi15 <= 25) and (near_sup or price <= support + 0.05):
        idea = "🔺 *תסריט לונג*"
        entry = min(price, support + 0.03)
        sl = support - 0.30
        tp1 = support + 0.50  # 148.50
        tp2 = support + 0.80  # 148.80
    else:
        idea = "😐 אין קצה ברור כרגע. עדיף להמתין להתקרבות ל־149.00/148.00 או קיצון RSI."

    msg_lines.append(idea)
    if entry:
        rr = (abs(entry - tp1)) / (abs(sl - entry)) if sl and tp1 else None
        msg_lines += [
            f"כניסה: *{entry:.3f}*",
            f"סטופ־לוס: *{sl:.3f}*",
            f"TP1: *{tp1:.3f}* | TP2: *{tp2:.3f}*",
            f"יחס סיכון/סיכוי (ל-TP1): *{rr:.2f}*",
        ]

    msg_lines.append("\nℹ️ אלגוריתם פשוט לצרכי מידע — לא ייעוץ השקעות.")
    return "\n".join(msg_lines)

# -------- telegram handlers --------
def start(update, context):
    update.message.reply_text("🤖 הבוט פעיל. פקודות: /signal /price /ping")

def ping(update, context):
    update.message.reply_text("🏓 pong")

def price_cmd(update, context):
    try:
        p = get_price()
        update.message.reply_text(f"💱 {PAIR} מחיר נוכחי: {p:.3f}")
    except Exception as e:
        update.message.reply_text(f"⚠️ שגיאה בקריאת מחיר: {e}")

def signal_cmd(update, context):
    try:
        txt = plan_signal()
        update.message.reply_markdown(txt, disable_web_page_preview=True)
    except Exception as e:
        update.message.reply_text(f"⚠️ שגיאה ביצירת איתות: {e}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("price", price_cmd))
    dp.add_handler(CommandHandler("signal", signal_cmd))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    # ניסיונות רשת חוזרים אם יש חנק ב-Alpha Vantage
    for _ in range(3):
        try:
            main()
            break
        except Exception as e:
            print("Restart after error:", e)
            time.sleep(5)
