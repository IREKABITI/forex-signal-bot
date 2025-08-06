import os
import tensorflow as tf
import joblib
import logging
import numpy as np

MODEL_PATH = 'lstm_signal_model.h5'
SCALER_PATH = 'scaler.save'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model_and_scaler():
    """
    Load the ML model and scaler from disk.
    Returns (model, scaler) or (None, None) if files not found.
    """
    model = None
    scaler = None
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            logger.info(f"Loaded ML model from {MODEL_PATH}")
        else:
            logger.warning(f"Model file {MODEL_PATH} not found.")
        if os.path.exists(SCALER_PATH):
            scaler = joblib.load(SCALER_PATH)
            logger.info(f"Loaded scaler from {SCALER_PATH}")
        else:
            logger.warning(f"Scaler file {SCALER_PATH} not found.")
    except Exception as e:
        logger.error(f"Error loading model or scaler: {e}")
    return model, scaler

def ml_predict_confidence(model, scaler, data):
    """
    Given model, scaler and input data, return ML confidence score.
    Returns 0.0 if model/scaler not loaded or error occurs.
    
    Args:
        model: TensorFlow model
        scaler: Scikit-learn scaler
        data: numpy array of features (1D or 2D)
    
    Returns:
        float confidence score (0.0 to 1.0)
    """
    if model is None or scaler is None:
        logger.warning("ML model or scaler not loaded, returning 0 confidence.")
        return 0.0
    
    try:
        # Ensure data is 2D array for scaler
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        data_scaled = scaler.transform(data)
        pred = model.predict(data_scaled)
        # Assume output is single scalar confidence, e.g. sigmoid output
        confidence = float(pred[0][0])
        # Clamp between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        return confidence
    except Exception as e:
        logger.error(f"Error during ML prediction: {e}")
        return 0.0
