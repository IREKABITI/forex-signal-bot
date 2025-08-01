"""
#IREKABITI_FX - AI-Powered Multi-Market Trading Ecosystem
Main application entry point
"""

import asyncio
import threading
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from config.settings import Settings
from bots.telegram_bot import TelegramBot
from bots.discord_bot import DiscordBot
from api.mobile_api import app as mobile_api
from scheduler.tasks import TaskScheduler
from utils.logger import setup_logger
from database.db_manager import DatabaseManager

logger = setup_logger()

class TradingEcosystem:
    def __init__(self):
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        self.telegram_bot = TelegramBot()
        self.discord_bot = DiscordBot()
        self.scheduler = TaskScheduler()
        
    async def start_bots(self):
        """Start both Telegram and Discord bots"""
        try:
            # Start Telegram bot
            telegram_task = asyncio.create_task(self.telegram_bot.start())
            
            # Start Discord bot
            discord_task = asyncio.create_task(self.discord_bot.start())
            
            logger.info("🤖 #IREKABITI_FX Bots started successfully")
            
            # Wait for both bots to complete
            await asyncio.gather(telegram_task, discord_task)
            
        except Exception as e:
            logger.error(f"❌ Error starting bots: {e}")
            
    def start_api_server(self):
        """Start FastAPI server for mobile app"""
        try:
            uvicorn.run(
                mobile_api,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
        except Exception as e:
            logger.error(f"❌ Error starting API server: {e}")
            
    def start_scheduler(self):
        """Start task scheduler"""
        try:
            self.scheduler.start()
            logger.info("⏰ Task scheduler started")
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")

async def main():
    """Main application entry point"""
    logger.info("🚀 Starting #IREKABITI_FX Trading Ecosystem")
    
    ecosystem = TradingEcosystem()
    
    # Initialize database
    await ecosystem.db_manager.initialize()
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=ecosystem.start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=ecosystem.start_api_server)
    api_thread.daemon = True
    api_thread.start()
    
    # Start bots (main async task)
    await ecosystem.start_bots()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 #IREKABITI_FX Ecosystem shutting down...")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
