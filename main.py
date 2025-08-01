"""
Main execution script for #IREKABITI_FX bot
Handles scheduling, startup, and periodic signal dispatch
"""

import asyncio
import logging
import threading
from time import sleep
from datetime import datetime
from signal_generator import send_signals
from utils.settings import settings
from bots.telegram_bot import TelegramBot
from bots.discord_bot import DiscordBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

logger = logging.getLogger(__name__)
telegram_bot = TelegramBot()
discord_bot = DiscordBot()

# === Scheduler: Run signals every X seconds (default: 300s = 5min) ===
async def scheduler_loop():
    while True:
        try:
            logger.info("⏳ Running signal scan...")
            send_signals(settings.TRADING_PAIRS_FOREX + settings.TRADING_PAIRS_CRYPTO, settings.TIMEFRAMES)
        except Exception as e:
            logger.error(f"❌ Error generating signals: {e}")
        await asyncio.sleep(settings.SIGNAL_CHECK_INTERVAL)

# === Bot Startup ===
def startup_alert():
    message = (
        "🚀 #IREKABITI_FX BOT STARTED\n"
        f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
        f"📡 Scanning markets every {settings.SIGNAL_CHECK_INTERVAL // 60} min\n"
        "#IRE_DID_THIS"
    )
    telegram_bot.send_message(message)
    discord_bot.send_message(message)
    logger.info("✅ Startup alert sent.")

# === Launch in Thread (for non-blocking bots or future dashboard use) ===
def launch_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scheduler_loop())

# === Main Entry Point ===
if __name__ == "__main__":
    logger.info("🔧 Launching #IREKABITI_FX bot...")
    startup_alert()
    threading.Thread(target=launch_async_loop).start()