import requests
import logging

TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

def send_discord_message(message):
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
    except Exception as e:
        logging.error(f"Discord send failed: {e}")

def send_alerts(message):
    send_telegram_message(message)
    send_discord_message(message)
