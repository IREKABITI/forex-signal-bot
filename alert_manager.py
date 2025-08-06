# alert_manager.py
import requests
import logging

# === Embedded User Config ===
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Telegram alert failed: {response.text}")
        else:
            logging.info("Telegram alert sent.")
    except Exception as e:
        logging.error(f"Telegram alert error: {e}")

def send_discord_alert(message):
    try:
        payload = {
            "content": message
        }
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code != 204 and response.status_code != 200:
            logging.error(f"Discord alert failed: {response.text}")
        else:
            logging.info("Discord alert sent.")
    except Exception as e:
        logging.error(f"Discord alert error: {e}")

def send_alerts(message):
    send_telegram_alert(message)
    send_discord_alert(message)
