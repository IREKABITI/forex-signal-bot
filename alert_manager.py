import requests
import logging

TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1401965462941859871/rDJQ1XZU-qFtGuOf7b1fkXEMLICM1vCNjkhBtzZ0__yVpcBFrUH6NmWnrXihRdv3L-WZ'

def send_alerts(signals):
    for signal in signals:
        message = format_signal_message(signal)
        send_telegram_alert(message)
        send_discord_alert(message)

def format_signal_message(signal):
    confidence_level = "High" if signal['final_confidence'] > 0.7 else "Medium" if signal['final_confidence'] > 0.4 else "Low"
    emoji = "🟢" if signal['signal'] == "Buy" else "🔴" if signal['signal'] == "Sell" else "⚪"
    msg = (
        f"{emoji} {signal['asset']} {signal['signal']} Signal\n"
        f"Confidence: {signal['final_confidence']:.2f} ({confidence_level})\n"
        f"ML Confidence: {signal['ml_confidence']:.2f}\n"
        f"Base Score: {signal['confidence']:.2f}\n"
        f"#IRE_DID_THIS"
    )
    return msg

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
        logging.info("✅ Telegram alert sent.")
    except Exception as e:
        logging.error(f"❌ Telegram alert failed: {e}")

def send_discord_alert(message):
    data = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=data)
        logging.info("✅ Discord alert sent.")
    except Exception as e:
        logging.error(f"❌ Discord alert failed: {e}")
