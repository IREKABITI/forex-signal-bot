import logging
import requests

# Your Telegram and Discord credentials - hardcoded
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info(f"Telegram message sent: {message}")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

def send_discord_message(message: str):
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        response.raise_for_status()
        logging.info(f"Discord message sent: {message}")
    except Exception as e:
        logging.error(f"Failed to send Discord message: {e}")

def format_signal_message(asset: str, signal: str, confidence: float):
    # Example formatter for signals with emojis based on confidence
    if confidence >= 0.75:
        emoji = "🟢"
        level = "High"
    elif confidence >= 0.5:
        emoji = "🟡"
        level = "Medium"
    else:
        emoji = "🔴"
        level = "Low"
    return f"{emoji} {asset} Signal: *{signal}* ({level} Confidence: {confidence:.2f})"

# Add any other helper functions here as needed for your bot...
