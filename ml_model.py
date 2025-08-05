import logging
import numpy as np
from tensorflow.keras.models import load_model
from joblib import load

# Try loading ML model and scaler
try:
    model = load_model('lstm_signal_model.h5')
    scaler = load('scaler.save')
    logging.info("✅ ML model and scaler loaded successfully.")
except Exception as e:
    model = None
    scaler = None
    logging.warning(f"⚠️ ML model or scaler files not found, ML confidence disabled.")

def get_ml_confidence_score(signal_data):
    if not model or not scaler:
        return 0.0  # fallback if model is missing
    
    try:
        features = np.array([
            signal_data.get('confidence', 0.5),
            1 if signal_data.get('signal') == 'Buy' else -1 if signal_data.get('signal') == 'Sell' else 0
        ]).reshape(1, -1)
        scaled = scaler.transform(features)
        confidence = model.predict(scaled)[0][0]
        return round(float(confidence), 2)
    except Exception as e:
        logging.error(f"❌ ML prediction failed: {e}")
        return 0.0
