import asyncio
from telegram import Bot
from telegram.error import TelegramError
from utils.logger import setup_logger

logger = setup_logger()

# Hardcoded token and chat ID
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)

    async def start(self):
        logger.info("📲 Telegram bot is active.")
        while True:
            await asyncio.sleep(10)  # keep alive loop

    async def send_signal(self, message: str):
        try:
            await self.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            logger.info("📤 Telegram signal sent")
        except TelegramError as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")