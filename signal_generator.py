import numpy as np
import tensorflow as tf
import joblib
import logging

# Load ML model and scaler once
MODEL_PATH = "lstm_signal_model.h5"
SCALER_PATH = "scaler.save"

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    logging.info("ML model and scaler loaded successfully.")
except Exception as e:
    model = None
    scaler = None
    logging.error(f"Failed to load ML model or scaler: {e}")

def get_ml_confidence(signal_features: dict) -> float:
    if model is None or scaler is None:
        logging.warning("ML model or scaler not loaded, returning 0 confidence.")
        return 0.0

    feature_order = ['technical_score', 'sentiment_score', 'news_score', 'combined_confidence']
    X = np.array([[signal_features.get(f, 0) for f in feature_order]])
    X_scaled = scaler.transform(X)
    X_input = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
    preds = model.predict(X_input)
    confidence = float(np.max(preds[0]))  # max probability for predicted class
    return confidence

def generate_signal_with_ml(input_data: dict):
    """
    input_data must include keys:
     - technical_score, sentiment_score, news_score, combined_confidence
     - other info for your signal generation

    Returns a dict including ML confidence.
    """

    # Your existing signal generation logic here
    # For example, determine base confidence score:
    base_confidence = input_data.get("combined_confidence", 0)

    # Add ML confidence
    ml_confidence = get_ml_confidence(input_data)

    # Combine or weight them as you like:
    final_confidence = (base_confidence + ml_confidence * 6) / 7  # Example weighting

    signal = {
        "signal": "Buy" if final_confidence > 0.6 else "Hold",
        "final_confidence": final_confidence,
        "ml_confidence": ml_confidence,
        "base_confidence": base_confidence,
        # Add other signal details as needed
    }

    logging.info(f"Generated signal: {signal}")
    return signal

# Example usage inside your scanning routine:
if __name__ == "__main__":
    example_input = {
        "technical_score": 0.8,
        "sentiment_score": 0.7,
        "news_score": 0.6,
        "combined_confidence": 0.75,
    }
    result = generate_signal_with_ml(example_input)
    print(result)
