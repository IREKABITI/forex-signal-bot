# ml_model.py
import numpy as np
import os
import logging

from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import ta

# Load model and scaler
model_path = "lstm_signal_model.h5"
scaler_path = "scaler.npy"

try:
    model = load_model(model_path)
    scaler = np.load(scaler_path, allow_pickle=True).item()
    logging.info("✅ ML model and scaler loaded.")
except Exception as e:
    logging.warning(f"⚠️ ML model or scaler files not found, ML confidence disabled. {e}")
    model = None
    scaler = None

def get_features(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1h", progress=False)
        if len(data) < 50:
            return None

        df = data.copy()
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["macd"] = ta.trend.MACD(df["Close"]).macd_diff()
        df["atr"] = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"]).average_true_range()
        df.dropna(inplace=True)

        features = df[["rsi", "macd", "atr"]].tail(50).values
        return features
    except Exception as e:
        logging.error(f"⚠️ Failed to fetch features for {ticker}: {e}")
        return None

def get_ml_confidence(ticker):
    if model is None or scaler is None:
        return 0.0  # fallback

    features = get_features(ticker)
    if features is None or len(features) < 50:
        return 0.0

    try:
        scaled = scaler.transform(features)
        input_data = scaled.reshape(1, 50, 3)
        prediction = model.predict(input_data, verbose=0)[0][0]
        return float(round(prediction, 2))
    except Exception as e:
        logging.error(f"⚠️ ML prediction failed for {ticker}: {e}")
        return 0.0
