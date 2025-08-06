from assets.eurusd_signal import generate_eurusd_signal_with_score
from alert_manager import send_alerts
import logging

def generate_signal_with_ml():
    signals = []
    try:
        eurusd = generate_eurusd_signal_with_score()
        signals.append(("EURUSD", eurusd))
    except Exception as e:
        logging.error(f"Error generating EURUSD signal: {e}")

    # Add other assets signals here if needed

    for symbol, data in signals:
        msg = f"🟢 {symbol} Signal: {data['signal']} (Score: {data['total_score']})\nDetails: {data['scores']}"
        logging.info(msg)
        send_alerts(msg)
