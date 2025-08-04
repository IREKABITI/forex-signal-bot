import schedule
import time
import logging
from main import run_full_scan

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def job():
    logging.info("🕒 Scheduled task started: Running full signal scan...")
    run_full_scan()

if __name__ == "__main__":
    logging.info("Scheduler started: running scan every 30 minutes.")
    schedule.every(30).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
