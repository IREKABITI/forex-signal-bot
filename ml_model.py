import os
import logging
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from data_prep import prepare_ml_features

logger = logging.getLogger(__name__)

MODEL_PATH = "lstm_signal_model.h5"
SCALER_PATH = "scaler.pkl"

model = None
scaler = None

def load_ml_model():
    global model, scaler
    try:
        if os.path.exists(MODEL_PATH):
            model = load_model(MODEL_PATH)
            logger.info("✅ ML model loaded successfully.")
        else:
            logger.warning("⚠️ ML model not found.")

        if os.path.exists(SCALER_PATH):
            import joblib
            scaler = joblib.load(SCALER_PATH)
            logger.info("✅ Scaler loaded successfully.")
        else:
            logger.warning("⚠️ Scaler not found.")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model or scaler: {e}")

def predict_confidence(df: pd.DataFrame) -> float:
    """
    Predict confidence score using ML model (0 to 1).
    """
    global model, scaler
    try:
        if model is None or scaler is None:
            logger.warning("⚠️ ML model or scaler files not found, ML confidence disabled.")
            return 0.0

        features_df = prepare_ml_features(df)
        if features_df.empty:
            return 0.0

        latest_features = features_df.tail(1).values
        scaled_features = scaler.transform(latest_features)
        prediction = model.predict(scaled_features)
        confidence_score = float(np.clip(prediction[0][0], 0, 1))
        return confidence_score
    except Exception as e:
        logger.error(f"❌ ML confidence prediction failed: {e}")
        return 0.0
