import datetime
import pytz
import logging
import requests

# Telegram and Discord credentials
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

# Trading sessions in UTC
SESSIONS = {
    'London': (datetime.time(7, 0), datetime.time(16, 0)),
    'New_York': (datetime.time(12, 0), datetime.time(21, 0)),
    'Tokyo': (datetime.time(0, 0), datetime.time(9, 0)),
    'Sydney': (datetime.time(22, 0), datetime.time(7, 0)),
}

def get_current_session():
    try:
        now_utc = datetime.datetime.utcnow().time()
        for session, (start, end) in SESSIONS.items():
            if start < end:
                if start <= now_utc < end:
                    return session
            else:  # Overnight session
                if now_utc >= start or now_utc < end:
                    return session
        return 'Off_Session'
    except Exception as e:
        logging.error(f"Error determining current trading session: {e}")
        send_telegram_alert(f"⚠️ Error determining current trading session: {e}")
        send_discord_alert(f"⚠️ Error determining current trading session: {e}")
        return 'Unknown'

def is_session_active(session_name):
    current = get_current_session()
    return current == session_name

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            logging.info("Telegram session alert sent successfully.")
        else:
            logging.warning(f"Telegram session alert failed with status {r.status_code}.")
    except Exception as e:
        logging.error(f"Error sending Telegram session alert: {e}")

def send_discord_alert(message):
    try:
        payload = {'content': message}
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if r.status_code == 204:
            logging.info("Discord session alert sent successfully.")
        else:
            logging.warning(f"Discord session alert failed with status {r.status_code}.")
    except Exception as e:
        logging.error(f"Error sending Discord session alert: {e}")
