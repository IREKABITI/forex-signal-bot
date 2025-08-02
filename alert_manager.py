# alert_manager.py
import requests
import base64
import io
import matplotlib.pyplot as plt

TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1398658870980644985/0fHPvafJv0Bi6uc0RzPITEzcKgqKt6znfhhrBy-4qFBas8BfxiTxjyFkVqtp_ctt-Ndt'

def send_alerts(signal, config):
    message = format_message(signal)
    send_telegram(message)
    send_discord(message)

def format_message(signal):
    emojis = {'High': '🟢', 'Medium': '🟠', 'Low': '🟥'}
    emoji = emojis.get(signal['confidence'], '❓')
    details = signal['details']
    details_str = " | ".join(
        f"{k} {'✅' if v else '❌'}" for k, v in details.items()
    )
    msg = (
        f"{emoji} {signal['asset']} {signal['direction']} Signal ({signal['score']}/8 Confidence)\n"
        f"Risk: {risk_level(signal['confidence'])}\n"
        f"Score Breakdown:\n{details_str}\n"
        f"#IRE_DID_THIS"
    )
    return msg

def risk_level(confidence):
    return {
        'High': 'Low Risk',
        'Medium': 'Moderate Risk',
        'Low': 'High Risk'
    }.get(confidence, 'Unknown Risk')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram send failed: {e}")

def send_discord(message):
    payload = {'content': message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Discord send failed: {e}")
