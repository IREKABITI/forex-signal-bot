# ===============================
# utils/indicators.py
# ===============================
import ta
import pandas as pd

def get_rsi_score(data):
    rsi = ta.momentum.RSIIndicator(data['Close']).rsi()
    last_rsi = rsi.iloc[-1]
    if last_rsi < 30:
        return 1  # Buy
    elif last_rsi > 70:
        return 1  # Sell
    return 0  # Neutral

def get_macd_score(data):
    macd = ta.trend.MACD(data['Close'])
    hist = macd.macd_diff()
    if hist.iloc[-1] > 0:
        return 1  # Buy
    elif hist.iloc[-1] < 0:
        return 1  # Sell
    return 0

def get_candle_score(data):
    last = data.iloc[-1]
    if last['Close'] > last['Open']:
        return 1  # Bullish candle
    elif last['Close'] < last['Open']:
        return 1  # Bearish candle
    return 0

def get_volatility_score(data):
    vol = data['Close'].rolling(window=14).std()
    return 1 if vol.iloc[-1] > vol.mean() else 0
