import logging
import time
from signal_generator import run_full_scan
from alert_manager import send_telegram_alert, send_discord_alert

# Your Telegram and Discord credentials here
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

logging.basicConfig(level=logging.INFO)

def main_loop():
    logging.info("🚀 Forex Signal Bot Started")

    while True:
        try:
            logging.info("🔍 Running full signal scan...")
            signals = run_full_scan()  # Should return list/dict of signals with confidence & details
            
            for signal in signals:
                message = (
                    f"🟢 {signal['asset']} {signal['signal']} Signal "
                    f"({signal['confidence']}/6 Confidence)\n"
                    f"Score Breakdown: RSI={signal['rsi_score']}, MACD={signal['macd_score']}, "
                    f"Candle={signal['candle_score']}, Volatility={signal['vol_score']}"
                )
                # Send alerts to Telegram and Discord
                send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)
                send_discord_alert(DISCORD_WEBHOOK, message)

        except Exception as e:
            logging.error(f"Error during signal scan: {e}")

        logging.info("⏳ Sleeping for 30 minutes before next scan...")
        time.sleep(1800)  # Sleep 30 minutes

if __name__ == "__main__":
    main_loop()
