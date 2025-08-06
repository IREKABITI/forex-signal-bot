import requests
import logging

# Your Telegram bot token and chat ID
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'

# Your Discord webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def send_telegram_message(message: str) -> bool:
    """Send message to Telegram chat."""
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logging.info(f"Telegram alert sent: {message}")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def send_discord_message(message: str) -> bool:
    """Send message to Discord webhook."""
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        logging.info(f"Discord alert sent: {message}")
        return True
    except Exception as e:
        logging.error(f"Failed to send Discord message: {e}")
        return False

def format_signal_alert(asset: str, signal: str, confidence: int, confidence_level: str, score_breakdown: dict) -> str:
    """Format signal alert message with emoji, confidence, and score breakdown."""
    emoji = {
        'High': '🟢',
        'Medium': '🟡',
        'Low': '🔴'
    }.get(confidence_level, '⚪')

    breakdown_str = ', '.join([f"{k}: {v}" for k, v in score_breakdown.items()])
    message = (
        f"{emoji} *{asset}* {signal} Signal ({confidence}/6 Confidence: {confidence_level})\n"
        f"Score breakdown: {breakdown_str}"
    )
    return message

# Add more helper functions as needed below
