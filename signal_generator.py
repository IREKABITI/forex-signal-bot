# signal_generator.py
import logging
from assets.eurusd_signal import generate_eurusd_signal_with_score
from assets.usdjpy_signal import generate_usdjpy_signal_with_score
from assets.gold_signal import generate_gold_signal_with_score
from ml_model import load_model_and_scaler, ml_predict_confidence

# Load ML model & scaler once
model, scaler = load_model_and_scaler()

# Threshold for accepting a signal (0.5 = 50% confidence)
CONFIDENCE_THRESHOLD = 0.5

def generate_signal_with_ml():
    signals = []
    for symbol, generator in [
        ("EURUSD", generate_eurusd_signal_with_score),
        ("USDJPY", generate_usdjpy_signal_with_score),
        ("GOLD", generate_gold_signal_with_score),
    ]:
        try:
            base_signal_data = generator()
            base_confidence = base_signal_data["confidence"]
            signal_type = base_signal_data["signal"]

            # ML Confidence
            if model and scaler:
                ml_conf = ml_predict_confidence(symbol, model, scaler)
            else:
                ml_conf = 0.0

            # Weighted final confidence
            final_confidence = round((base_confidence + ml_conf) / 2, 2)

            # Accept or reject based on confidence
            if final_confidence >= CONFIDENCE_THRESHOLD:
                msg = f"🟢 {symbol} {signal_type} Signal ({final_confidence*100:.0f}% Confidence)"
                signals.append({
                    "symbol": symbol,
                    "signal": signal_type,
                    "confidence": final_confidence,
                    "ml_confidence": ml_conf,
                    "base_confidence": base_confidence,
                    "message": msg,
                    "status": "accepted"
                })
            else:
                signals.append({
                    "symbol": symbol,
                    "signal": signal_type,
                    "confidence": final_confidence,
                    "ml_confidence": ml_conf,
                    "base_confidence": base_confidence,
                    "status": "rejected"
                })

        except Exception as e:
            logging.error(f"❌ Error generating signal for {symbol}: {e}")
    
    return signals

#IRE_DID_THIS
