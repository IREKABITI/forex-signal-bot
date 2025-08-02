# main.py
import time
from signal_generator import generate_signals
from alert_manager import send_alerts
from config import Config

def main():
    config = Config()
    scan_interval = config.get('scan_interval', 300)  # seconds

    while True:
        signals = generate_signals(config)
        for signal in signals:
            if signal['score'] >= config.get('min_score', 4):
                send_alerts(signal, config)
        time.sleep(scan_interval)

if __name__ == "__main__":
    main()
