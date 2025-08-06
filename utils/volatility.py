import yfinance as yf
import logging
import requests

# Telegram and Discord credentials
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def get_volatility(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1d", auto_adjust=True)
        if data.empty or 'Close' not in data:
            logging.warning(f"No data found for volatility calculation: {ticker}")
            return None
        high = data['High']
        low = data['Low']
        close = data['Close']

        # Calculate True Range
        tr = high.combine(low, max) - low.combine(close.shift(1), min)
        atr = tr.rolling(window=14).mean().iloc[-1]
        if atr is None or atr != atr:  # Check for NaN
            logging.warning(f"ATR calculation returned NaN for {ticker}")
            return None
        return atr
    except Exception as e:
        logging.error(f"Error calculating volatility for {ticker}: {e}")
        send_telegram_alert(f"⚠️ Error calculating volatility for {ticker}: {e}")
        send_discord_alert(f"⚠️ Error calculating volatility for {ticker}: {e}")
        return None

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
