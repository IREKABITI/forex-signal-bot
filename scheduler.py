# scheduler.py
import threading
import logging
from signal_generator import run_full_scan

def schedule_scans(interval_minutes=5):
    """Schedules run_full_scan to run every interval_minutes."""
    def run_periodically():
        try:
            logging.info(f"⏳ Running scheduled signal scan...")
            run_full_scan()
        except Exception as e:
            logging.error(f"❌ Error during scheduled scan: {e}")
        
        # Schedule the next scan
        threading.Timer(interval_minutes * 60, run_periodically).start()

    # Start the first scheduled run
    run_periodically()
