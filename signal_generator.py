import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import pandas as pd

MODEL_PATH = "lstm_signal_model.h5"

# Load your trained model once (e.g., at module load)
model = tf.keras.models.load_model(MODEL_PATH)
scaler = None  # We'll load or fit scaler later

def load_scaler(X_train):
    # Fit scaler on training data features
    global scaler
    scaler = StandardScaler()
    scaler.fit(X_train)

def get_ml_confidence(signal_features: dict) -> float:
    """
    Takes a dict of features (technical_score, sentiment_score, news_score, etc.)
    Returns model confidence (probability of predicted class) as float between 0-1.
    """

    # Prepare input vector from features in correct order matching training data
    feature_order = ['technical_score', 'sentiment_score', 'news_score', 'combined_confidence']
    X = np.array([[signal_features.get(f, 0) for f in feature_order]])

    # Scale features
    if scaler is None:
        raise RuntimeError("Scaler not loaded or fitted")

    X_scaled = scaler.transform(X)

    # Reshape for LSTM input: (samples, timesteps, features)
    X_input = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

    # Predict probabilities
    preds = model.predict(X_input)
    confidence = np.max(preds[0])  # Max probability across classes

    return confidence
