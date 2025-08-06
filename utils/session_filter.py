import datetime
import pytz
import logging
import requests

# Telegram and Discord credentials
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

# Timezone info for sessions
LONDON_TZ = pytz.timezone('Europe/London')
NEW_YORK_TZ = pytz.timezone('America/New_York')

def get_current_utc_time():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

def is_london_session():
    now = get_current_utc_time().astimezone(LONDON_TZ)
    start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    in_session = start <= now <= end
    logging.debug(f"London session check: {now} - {in_session}")
    return in_session

def is_new_york_session():
    now = get_current_utc_time().astimezone(NEW_YORK_TZ)
    start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)
    in_session = start <= now <= end
    logging.debug(f"New York session check: {now} - {in_session}")
    return in_session

def current_session():
    if is_london_session():
        return 'London'
    elif is_new_york_session():
        return 'New York'
    else:
        return 'Off-Session'

def notify_session_status():
    session = current_session()
    message = f"⏰ Current Trading Session: {session}"
    send_telegram_alert(message)
    send_discord_alert(message)
    logging.info(message)

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
