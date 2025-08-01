"""
Discord Bot for #IREKABITI_FX
"""

import requests
import logging

# === HARDCODED DISCORD WEBHOOK ===
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1398658870980644985/0fHPvafJv0Bi6uc0RzPITEzcKgqKt6znfhhrBy-4qFBas8BfxiTxjyFkVqtp_ctt-Ndt"

logger = logging.getLogger(__name__)


class DiscordBot:
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL

    def send_message(self, content: str):
        try:
            response = requests.post(self.webhook_url, json={"content": content})
            if response.status_code == 204:
                logger.info("✅ Discord message sent successfully.")
            else:
                logger.error(f"❌ Discord error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"❌ Discord send error: {e}")


# Optional: Standalone testing
if __name__ == "__main__":
    bot = DiscordBot()
    bot.send_message("🚀 Test signal from #IREKABITI_FX")