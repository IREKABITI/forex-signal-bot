import logging
import time
from signal_generator import run_full_scan
from alert_manager import send_telegram_alert, send_discord_alert

# Your hardcoded tokens (replace with your actual tokens)
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def main_loop():
    logger.info("🚀 Forex Signal Bot Started")
    while True:
        logger.info("🔍 Running full signal scan...")
        signals = run_full_scan()

        for asset, signal_info in signals.items():
            # Build alert message
            message = f"📊 {asset} Signal:\n"
            message += f"Signal: {signal_info.get('signal')}\n"
            message += f"Confidence: {signal_info.get('final_confidence', 0):.2f}\n"
            message += f"Details: {signal_info}"

            try:
                # Send alerts
                send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)
                send_discord_alert(DISCORD_WEBHOOK_URL, message)
                logger.info(f"✅ Sent alert for {asset}")
            except Exception as e:
                logger.error(f"Failed to send alert for {asset}: {e}")

        logger.info("⏳ Sleeping for 30 minutes before next scan...")
        time.sleep(1800)  # Sleep for 30 minutes

if __name__ == "__main__":
    main_loop()
