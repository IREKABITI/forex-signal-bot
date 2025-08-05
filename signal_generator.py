import logging
from assets.gold_signal import generate_gold_signal_with_score
from assets.eurusd_signal import generate_eurusd_signal_with_score
from assets.usdjpy_signal import generate_usdjpy_signal_with_score
from alert_manager import send_alerts
from ml_model import get_ml_confidence_score

# Confidence threshold to filter weak signals
MIN_CONFIDENCE = 0.3

def run_full_scan():
    logging.info("🔍 Running full signal scan...")
    
    all_signals = []

    # Gold Signal
    gold_signal = generate_gold_signal_with_score()
    gold_signal['ml_confidence'] = get_ml_confidence_score(gold_signal)
    gold_signal['final_confidence'] = (gold_signal['confidence'] + gold_signal['ml_confidence']) / 2
    if gold_signal['final_confidence'] >= MIN_CONFIDENCE:
        all_signals.append(gold_signal)
        logging.info(f"✅ Sending alert: {gold_signal}")
    else:
        logging.info(f"❌ Signal 'Gold' rejected due to low confidence ({gold_signal['final_confidence']:.2f})")

    # EURUSD Signal
    eurusd_signal = generate_eurusd_signal_with_score()
    eurusd_signal['ml_confidence'] = get_ml_confidence_score(eurusd_signal)
    eurusd_signal['final_confidence'] = (eurusd_signal['confidence'] + eurusd_signal['ml_confidence']) / 2
    if eurusd_signal['final_confidence'] >= MIN_CONFIDENCE:
        all_signals.append(eurusd_signal)
        logging.info(f"✅ Sending alert: {eurusd_signal}")
    else:
        logging.info(f"❌ Signal 'EURUSD' rejected due to low confidence ({eurusd_signal['final_confidence']:.2f})")

    # USDJPY Signal
    usdjpy_signal = generate_usdjpy_signal_with_score()
    usdjpy_signal['ml_confidence'] = get_ml_confidence_score(usdjpy_signal)
    usdjpy_signal['final_confidence'] = (usdjpy_signal['confidence'] + usdjpy_signal['ml_confidence']) / 2
    if usdjpy_signal['final_confidence'] >= MIN_CONFIDENCE:
        all_signals.append(usdjpy_signal)
        logging.info(f"✅ Sending alert: {usdjpy_signal}")
    else:
        logging.info(f"❌ Signal 'USDJPY' rejected due to low confidence ({usdjpy_signal['final_confidence']:.2f})")

    if all_signals:
        send_alerts(all_signals)
