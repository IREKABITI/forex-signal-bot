import yfinance as yf
import numpy as np
import logging
import requests

# Telegram and Discord credentials
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def calculate_atr(high, low, close, period=14):
    tr_list = []
    for i in range(1, len(close)):
        tr = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        tr_list.append(tr)
    atr = np.mean(tr_list[-period:])
    return atr

def get_volatility_score(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
        if data.empty:
            logging.warning(f"No data returned for ticker {ticker} in volatility.py")
            return 0

        high = data['High'].values
        low = data['Low'].values
        close = data['Close'].values

        atr = calculate_atr(high, low, close)
        avg_close = np.mean(close[-14:])
        volatility = atr / avg_close if avg_close != 0 else 0

        # Score interpretation:
        # Low volatility: <0.01 = score 1
        # Medium volatility: 0.01 - 0.02 = score 2
        # High volatility: >0.02 = score 3
        if volatility < 0.01:
            score = 1
        elif volatility < 0.02:
            score = 2
        else:
            score = 3

        logging.info(f"Volatility for {ticker}: ATR={atr:.4f}, Volatility={volatility:.4f}, Score={score}")
        return score
    except Exception as e:
        logging.error(f"Error calculating volatility for {ticker}: {e}")
        send_telegram_alert(f"⚠️ Error calculating volatility for {ticker}: {e}")
        send_discord_alert(f"⚠️ Error calculating volatility for {ticker}: {e}")
        return 0

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            logging.info("Telegram volatility alert sent successfully.")
        else:
            logging.warning(f"Telegram volatility alert failed with status {r.status_code}.")
    except Exception as e:
        logging.error(f"Error sending Telegram volatility alert: {e}")

def send_discord_alert(message):
    try:
        payload = {'content': message}
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if r.status_code == 204:
            logging.info("Discord volatility alert sent successfully.")
        else:
            logging.warning(f"Discord volatility alert failed with status {r.status_code}.")
    except Exception as e:
        logging.error(f"Error sending Discord volatility alert: {e}")
