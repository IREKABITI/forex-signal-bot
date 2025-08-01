import aiohttp
from utils.logger import setup_logger

logger = setup_logger()

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1398658870980644985/0fHPvafJv0Bi6uc0RzPITEzcKgqKt6znfhhrBy-4qFBas8BfxiTxjyFkVqtp_ctt-Ndt"

class DiscordBot:
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL

    async def send_signal(self, message: str):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"content": message}
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("📤 Discord signal sent")
                    else:
                        logger.error(f"❌ Discord error {response.status}: {await response.text()}")
        except Exception as e:
            logger.error(f"❌ Failed to send Discord message: {e}")