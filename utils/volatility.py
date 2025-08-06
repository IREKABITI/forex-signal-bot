import yfinance as yf
import numpy as np
import logging
import requests

TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

def fetch_price_data(ticker, period="1mo", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    if data.empty:
        logging.error(f"No data fetched for {ticker}")
    return data

def calculate_atr(data, period=14):
    high = data['High']
    low = data['Low']
    close = data['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = np.maximum(np.maximum(tr1, tr2), tr3)
    atr = tr.rolling(window=period).mean()
    return atr

def calculate_volatility(ticker):
    data = fetch_price_data(ticker)
    if data.empty:
        return None
    atr = calculate_atr(data)
    latest_atr = atr.iloc[-1] if not atr.empty else None
    return latest_atr

def send_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    discord_url = DISCORD_WEBHOOK

    # Telegram alert
    try:
        resp = requests.post(telegram_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        resp.raise_for_status()
        logging.info("Telegram alert sent.")
    except Exception as e:
        logging.error(f"Telegram alert failed: {e}")

    # Discord alert
    try:
        resp = requests.post(discord_url, json={"content": message})
        resp.raise_for_status()
        logging.info("Discord alert sent.")
    except Exception as e:
        logging.error(f"Discord alert failed: {e}")

if __name__ == "__main__":
    test_ticker = "EURUSD=X"
    vol = calculate_volatility(test_ticker)
    if vol:
        msg = f"📊 Current ATR volatility for {test_ticker}: {vol:.5f}"
        send_alert(msg)
