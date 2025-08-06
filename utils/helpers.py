import requests
import logging

# Hardcoded Telegram and Discord credentials
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def send_telegram_message(message: str) -> bool:
    """Send a message to Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info(f"✅ Telegram message sent: {message}")
        return True
    except requests.RequestException as e:
        logging.error(f"❌ Telegram message failed: {e}")
        return False

def send_discord_message(message: str) -> bool:
    """Send a message to Discord webhook."""
    payload = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"✅ Discord message sent: {message}")
        return True
    except requests.RequestException as e:
        logging.error(f"❌ Discord message failed: {e}")
        return False

def format_signal_alert(asset: str, signal: str, score: int, confidence_level: str) -> str:
    """Create a formatted alert message with emoji and score."""
    emoji_map = {
        'High': '🟢',
        'Medium': '🟡',
        'Low': '🔴'
    }
    emoji = emoji_map.get(confidence_level, '⚪')
    return f"{emoji} {asset} {signal} Signal ({score}/6 Confidence: {confidence_level})"

# Add any other helper functions here as needed
