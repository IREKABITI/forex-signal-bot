# alert_manager.py
import requests
import logging

TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
CHAT_ID = '5689209090'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1401965462941859871/rDJQ1XZU-qFtGuOf7b1fkXEMLICM1vCNjkhBtzZ0__yVpcBFrUH6NmWnrXihRdv3L-WZ'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Telegram alert failed: {response.text}")
    except Exception as e:
        logging.error(f"Telegram alert error: {e}")

def send_discord_alert(message):
    payload = {'content': message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if response.status_code != 204:
            logging.error(f"Discord alert failed: {response.text}")
    except Exception as e:
        logging.error(f"Discord alert error: {e}")

def send_alerts(message):
    send_telegram_alert(message)
    send_discord_alert(message)
