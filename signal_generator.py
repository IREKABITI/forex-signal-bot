# ===============================
# signal_generator.py
# ===============================
import logging
from assets.eurusd_signal import generate_eurusd_signal_with_score
from assets.usdjpy_signal import generate_usdjpy_signal_with_score
from assets.gold_signal import generate_gold_signal_with_score

def run_full_scan():
    logging.info("🔍 Running full signal scan...")
    try:
        generate_eurusd_signal_with_score()
    except Exception as e:
        logging.error(f"Error generating signal for EURUSD: {e}")
    try:
        generate_usdjpy_signal_with_score()
    except Exception as e:
        logging.error(f"Error generating signal for USDJPY: {e}")
    try:
        generate_gold_signal_with_score()
    except Exception as e:
        logging.error(f"Error generating signal for GOLD: {e}")
