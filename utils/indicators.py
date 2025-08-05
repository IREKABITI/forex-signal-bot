import yfinance as yf
import numpy as np
import pandas as pd
import ta

def download_data(ticker, period="1mo", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
    data.dropna(inplace=True)
    return data

def get_rsi_score(ticker, period=14):
    data = download_data(ticker)
    rsi_indicator = ta.momentum.RSIIndicator(close=data['Close'], window=period)
    rsi = rsi_indicator.rsi()
    latest_rsi = rsi.iloc[-1]

    # RSI scoring example
    if latest_rsi < 30:
        return 1  # Oversold - buy signal
    elif latest_rsi > 70:
        return -1  # Overbought - sell signal
    else:
        return 0  # Neutral

def get_macd_score(ticker, fast=12, slow=26, signal=9):
    data = download_data(ticker)
    macd_indicator = ta.trend.MACD(close=data['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
    macd_line = macd_indicator.macd()
    signal_line = macd_indicator.macd_signal()
    latest_macd = macd_line.iloc[-1]
    latest_signal = signal_line.iloc[-1]

    if latest_macd > latest_signal:
        return 1  # Bullish crossover
    elif latest_macd < latest_signal:
        return -1  # Bearish crossover
    else:
        return 0

def get_candle_score(ticker):
    data = download_data(ticker, period="5d")
    # Simple example: bullish if last close > open, bearish if close < open
    last_candle = data.iloc[-1]
    if last_candle['Close'] > last_candle['Open']:
        return 1
    elif last_candle['Close'] < last_candle['Open']:
        return -1
    else:
        return 0

def get_volatility_score(ticker, period=14):
    data = download_data(ticker)
    atr_indicator = ta.volatility.AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'], window=period)
    atr = atr_indicator.average_true_range()
    latest_atr = atr.iloc[-1]

    # Simple scoring based on ATR level (customize thresholds)
    if latest_atr > data['Close'].std():
        return 1  # High volatility - good for breakout
    else:
        return 0  # Low volatility

