# main.py
import logging
from signal_generator import generate_signal_with_ml
from alert_manager import send_alerts
from scheduler import start_scheduler

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run():
    logging.info("🚀 Forex Signal Bot Started")
    logging.info("🔍 Running full signal scan...")

    signals = generate_signal_with_ml()
    for signal_data in signals:
        if signal_data["status"] == "accepted":
            logging.info(f"✅ Sending alert: {signal_data['message']}")
            send_alerts(signal_data)
        else:
            logging.info(f"❌ Signal '{signal_data['symbol']}' rejected due to low confidence ({signal_data['confidence']})")

if __name__ == "__main__":
    run()
    start_scheduler()

#IRE_DID_THIS
