# utils/indicators.py
import yfinance as yf
import pandas as pd
import numpy as np
import ta  # pure Python technical analysis

# RSI Score
def get_rsi_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d", progress=False)
    if data.empty or 'Close' not in data:
        return 0
    rsi = ta.momentum.RSIIndicator(close=data['Close']).rsi().iloc[-1]
    if rsi < 30:
        return 1  # Oversold -> Buy signal
    elif rsi > 70:
        return -1  # Overbought -> Sell signal
    else:
        return 0  # Neutral

# MACD Score
def get_macd_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d", progress=False)
    if data.empty or 'Close' not in data:
        return 0
    macd = ta.trend.MACD(close=data['Close'])
    macd_diff = macd.macd_diff().iloc[-1]
    if macd_diff > 0:
        return 1  # Bullish
    elif macd_diff < 0:
        return -1  # Bearish
    else:
        return 0  # Neutral

# Candle Score (simple heuristic)
def get_candle_score(ticker):
    data = yf.download(ticker, period="5d", interval="1d", progress=False)
    if data.empty or len(data) < 2:
        return 0
    last = data.iloc[-1]
    open_price, close_price = last['Open'], last['Close']
    if close_price > open_price:
        return 1  # Bullish candle
    elif close_price < open_price:
        return -1  # Bearish candle
    else:
        return 0  # Doji or neutral

# Volatility Score using ATR
def get_volatility_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d", progress=False)
    if data.empty:
        return 0
    atr = ta.volatility.AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close']).average_true_range().iloc[-1]
    volatility = atr / data['Close'].iloc[-1]
    if volatility < 0.01:
        return 1  # Low volatility
    elif volatility > 0.03:
        return -1  # High volatility
    else:
        return 0  # Medium volatility
