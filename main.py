# main.py
import time
import logging
from signal_generator import run_full_scan
from scheduler import schedule_scans

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("🚀 Forex Signal Bot Started")

    try:
        # Run immediate scan
        run_full_scan()

        # Schedule scans every 5 minutes
        schedule_scans(interval_minutes=5)

        # Keep the bot running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped manually.")

    except Exception as e:
        logging.error(f"❌ Critical error: {e}")
