# scheduler.py
import schedule
import time
import logging
from signal_generator import generate_signal_with_ml

logging.basicConfig(level=logging.INFO)

def run_scheduled_scan():
    logging.info("📅 Running scheduled signal scan...")
    generate_signal_with_ml()

def start_scheduler():
    # Run scan every 30 minutes
    schedule.every(30).minutes.do(run_scheduled_scan)
    
    logging.info("✅ Scheduler started. Signals will run every 30 minutes.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logging.info("🚦 Starting Forex Signal Bot Scheduler")
    run_scheduled_scan()  # Initial scan on startup
    start_scheduler()
