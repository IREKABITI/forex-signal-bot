"""
Telegram Bot for #IREKABITI_FX
"""

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# === HARDCODED CREDENTIALS ===
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = 5689209090  # Your chat ID

# === BOT SETUP ===
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_message(self, message: str):
        try:
            await bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info("✅ Telegram message sent")
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")

    async def start(self):
        @dp.message_handler(commands=["start", "hello"])
        async def handle_start(message: types.Message):
            await message.reply("👋 Welcome to #IREKABITI_FX Signal Bot!")

        logger.info("📨 Telegram bot is running...")
        await dp.start_polling()


# Optional: Standalone testing
if __name__ == "__main__":
    import asyncio
    test_bot = TelegramBot()
    asyncio.run(test_bot.send_message("🚀 Test signal from #IREKABITI_FX"))