import numpy as np
import tensorflow as tf
import joblib
import logging
import os

MODEL_PATH = "lstm_signal_model.h5"
SCALER_PATH = "scaler.save"

logging.basicConfig(level=logging.INFO)

model = None
scaler = None

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logging.info("✅ ML model and scaler loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load ML model or scaler: {e}")
else:
    logging.warning("⚠️ ML model or scaler files not found, ML confidence disabled.")

def get_ml_confidence(signal_features: dict) -> float:
    if model is None or scaler is None:
        return 0.0

    feature_order = ['technical_score', 'sentiment_score', 'news_score', 'combined_confidence']
    try:
        X = np.array([[signal_features.get(f, 0) for f in feature_order]])
        X_scaled = scaler.transform(X)
        X_input = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        preds = model.predict(X_input)
        confidence = float(np.max(preds[0]))
        return confidence
    except Exception as e:
        logging.error(f"Error during ML prediction: {e}")
        return 0.0

def generate_signal_with_ml(input_data: dict):
    base_confidence = input_data.get("combined_confidence", 0)
    ml_confidence = get_ml_confidence(input_data)

    final_confidence = (base_confidence + ml_confidence * 6) / 7

    signal_label = "Buy" if final_confidence >= 0.6 else "Hold"

    signal = {
        "signal": signal_label,
        "final_confidence": final_confidence,
        "ml_confidence": ml_confidence,
        "base_confidence": base_confidence,
    }

    logging.info(f"Generated signal for {input_data.get('asset', 'Unknown')}: {signal}")
    return signal
