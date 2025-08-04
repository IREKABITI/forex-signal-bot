import requests
import logging

# Your Telegram and Discord credentials embedded here
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1401965462941859871/rDJQ1XZU-qFtGuOf7b1fkXEMLICM1vCNjkhBtzZ0__yVpcBFrUH6NmWnrXihRdv3L-WZ"

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info("Telegram alert sent successfully.")
        else:
            logging.error(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        logging.error(f"Telegram send error: {e}")

def send_discord_message(message: str):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            logging.info("Discord alert sent successfully.")
        else:
            logging.error(f"Failed to send Discord alert: {response.text}")
    except Exception as e:
        logging.error(f"Discord send error: {e}")

def send_signal_alert(signal_data: dict):
    asset = signal_data.get("asset", "Unknown")
    signal = signal_data.get("signal", "Hold")
    confidence = signal_data.get("final_confidence", 0)
    session = signal_data.get("session", "Unknown")
    tp = signal_data.get("tp", "N/A")
    sl = signal_data.get("sl", "N/A")

    if confidence >= 0.75:
        emoji = "🟢"
        conf_level = "High"
    elif confidence >= 0.5:
        emoji = "🟡"
        conf_level = "Medium"
    else:
        emoji = "🔴"
        conf_level = "Low"

    message = (
        f"{emoji} *{asset}* {signal} Signal\n"
        f"Confidence: {confidence:.2f} ({conf_level})\n"
        f"Session: {session}\n"
        f"TP: {tp}\n"
        f"SL: {sl}\n"
        f"#IRE_DID_THIS"
    )

    send_telegram_message(message)
    send_discord_message(message)
