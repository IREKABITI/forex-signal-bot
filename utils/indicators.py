# utils/indicators.py
import yfinance as yf
import numpy as np
import talib
import logging

logging.basicConfig(level=logging.INFO)

def get_rsi_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    close = data['Close'].values
    rsi = talib.RSI(close, timeperiod=14)
    if rsi[-1] < 30:
        return 1  # Buy signal
    elif rsi[-1] > 70:
        return -1  # Sell signal
    return 0  # Neutral

def get_macd_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    close = data['Close'].values
    macd, signal, _ = talib.MACD(close)
    if macd[-1] > signal[-1]:
        return 1  # Bullish
    elif macd[-1] < signal[-1]:
        return -1  # Bearish
    return 0  # Neutral

def get_candle_score(ticker):
    data = yf.download(ticker, period="5d", interval="1d")
    open_ = data['Open'].values[-1]
    close = data['Close'].values[-1]
    if close > open_:
        return 1  # Bullish candle
    elif close < open_:
        return -1  # Bearish candle
    return 0  # Doji / neutral

def get_volatility_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    close = data['Close'].values
    atr = talib.ATR(data['High'], data['Low'], close)[-1]
    if atr > np.mean(atr):
        return -1  # High volatility (risky)
    return 1  # Acceptable volatility
