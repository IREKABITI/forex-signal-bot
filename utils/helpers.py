# utils/helpers.py

import datetime
import logging
import requests

# Hardcoded Telegram and Discord credentials
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

def is_trading_session_now(session_name: str) -> bool:
    """
    Checks if the current time is within a trading session.
    session_name options: 'london', 'ny', 'asia', 'off'
    Times are UTC.
    """
    now = datetime.datetime.utcnow().time()

    sessions = {
        'london': (datetime.time(7, 0), datetime.time(16, 0)),
        'ny': (datetime.time(12, 0), datetime.time(21, 0)),
        'asia': (datetime.time(23, 0), datetime.time(8, 0)),
    }

    if session_name not in sessions:
        logging.warning(f"Unknown session name: {session_name}")
        return False

    start, end = sessions[session_name]
    if start < end:
        return start <= now < end
    else:  # crosses midnight
        return now >= start or now < end

def format_signal_message(signal_name, confidence, components_scores, emoji):
    """
    Formats the alert message for Telegram or Discord.
    components_scores is a dict with keys like 'RSI', 'MACD', 'News', etc.
    """
    comp_str = ", ".join([f"{k}: {v}" for k, v in components_scores.items()])
    message = f"{emoji} {signal_name} Signal ({confidence}/6 Confidence)\nDetails: {comp_str}"
    return message

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("✅ Telegram message sent")
    except Exception as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")

def send_discord_message(message: str):
    payload = {
        "content": message
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logging.info("✅ Discord message sent")
    except Exception as e:
        logging.error(f"❌ Failed to send Discord message: {e}")
