# signal_generator.py
import logging
from alert_manager import send_alerts
from assets.gold_signal import generate_gold_signal_with_score
from assets.eurusd_signal import generate_eurusd_signal_with_score
from assets.usdjpy_signal import generate_usdjpy_signal_with_score

# Minimum signal score to send alert (1 to 6)
MIN_SIGNAL_SCORE = 3

def run_full_scan():
    logging.info("🔍 Running full signal scan...")

    signals = []

    # Get signal + score from each asset
    gold_signal = generate_gold_signal_with_score()
    eurusd_signal = generate_eurusd_signal_with_score()
    usdjpy_signal = generate_usdjpy_signal_with_score()

    signals.extend([gold_signal, eurusd_signal, usdjpy_signal])

    # Process signals: filter, format, send alerts
    for sig in signals:
        if sig is None:
            continue

        score = sig.get('score', 0)
        signal_text = sig.get('signal', '')
        asset = sig.get('asset', 'Unknown')

        if score < MIN_SIGNAL_SCORE:
            logging.info(f"❌ Signal '{asset}' rejected due to low score ({score})")
            continue

        confidence = get_confidence_label(score)
        message = f"🟢 {asset} {signal_text} ({score}/6 Confidence: {confidence})"
        
        logging.info(f"✅ Sending alert: {message}")
        send_alerts(message)


def get_confidence_label(score):
    if score <= 2:
        return "Low"
    elif score <= 4:
        return "Medium"
    else:
        return "High"
