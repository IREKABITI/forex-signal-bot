import requests
import logging

# Your Telegram and Discord credentials (hardcoded)
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1401965462941859871/rDJQ1XZU-qFtGuOf7b1fkXEMLICM1vCNjkhBtzZ0__yVpcBFrUH6NmWnrXihRdv3L-WZ"

def format_confidence_emoji(confidence: float) -> str:
    if confidence >= 0.75:
        return "🔥"  # High confidence
    elif confidence >= 0.5:
        return "⚡"  # Medium confidence
    else:
        return "⚠️"  # Low confidence

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("Telegram alert sent successfully.")
    except Exception as e:
        logging.error(f"Telegram alert failed: {e}")

def send_discord_alert(message: str):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        response.raise_for_status()
        logging.info("Discord alert sent successfully.")
    except Exception as e:
        logging.error(f"Discord alert failed: {e}")

def send_signal_alert(signal_data: dict):
    """
    signal_data example:
    {
        "asset": "EURUSD",
        "signal": "Buy",
        "final_confidence": 0.82,
        "ml_confidence": 0.9,
        "base_confidence": 0.7,
        "tp": 1.1050,
        "sl": 1.0950,
        "session": "London"
    }
    """

    emoji = format_confidence_emoji(signal_data["final_confidence"])
    conf_percent = int(signal_data["final_confidence"] * 100)

    message = (
        f"{emoji} *{signal_data['asset']}* {signal_data['signal']} Signal\n"
        f"Confidence: {conf_percent}%\n"
        f"ML Confidence: {int(signal_data['ml_confidence']*100)}%\n"
        f"Base Confidence: {int(signal_data['base_confidence']*100)}%\n"
        f"TP: {signal_data.get('tp', 'N/A')}  SL: {signal_data.get('sl', 'N/A')}\n"
        f"Session: {signal_data.get('session', 'Unknown')}"
    )

    send_telegram_alert(message)
    send_discord_alert(message)
