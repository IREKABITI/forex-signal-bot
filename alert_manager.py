import requests
import logging

TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

logger = logging.getLogger(__name__)

def send_telegram_alert(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"✅ Telegram alert sent successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram alert: {e}")

def send_discord_alert(message: str) -> None:
    payload = {
        "content": message
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logger.info(f"✅ Discord alert sent successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to send Discord alert: {e}")

def send_alerts(message: str) -> None:
    logger.info(f"🚨 Sending alert: {message}")
    send_telegram_alert(message)
    send_discord_alert(message)
