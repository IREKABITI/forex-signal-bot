# utils/indicators.py

import pandas as pd
import yfinance as yf
import ta  # technical analysis library
import logging

def download_data(ticker, period="1mo", interval="1d", auto_adjust=True):
    """
    Downloads OHLCV data using yfinance with auto_adjust=True (adjusted close).
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust, progress=False)
        return data
    except Exception as e:
        logging.error(f"Failed to download data for {ticker}: {e}")
        return pd.DataFrame()

def get_rsi_score(ticker):
    data = download_data(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0

    rsi = ta.momentum.RSIIndicator(data['Close']).rsi()
    latest_rsi = rsi.iloc[-1]

    # Scoring logic: Strong buy if RSI < 30, strong sell if RSI > 70
    if latest_rsi < 30:
        return 1  # bullish signal
    elif latest_rsi > 70:
        return -1  # bearish signal
    return 0

def get_macd_score(ticker):
    data = download_data(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0

    macd_indicator = ta.trend.MACD(data['Close'])
    macd = macd_indicator.macd()
    signal = macd_indicator.macd_signal()

    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]

    # Bullish if MACD crosses above signal line, bearish if below
    if latest_macd > latest_signal:
        return 1
    elif latest_macd < latest_signal:
        return -1
    return 0

def get_candle_score(ticker):
    data = download_data(ticker, period="5d", interval="1d")
    if data.empty:
        return 0

    # Simple candlestick: bullish if close > open, bearish if close < open
    last_candle = data.iloc[-1]
    if last_candle['Close'] > last_candle['Open']:
        return 1
    elif last_candle['Close'] < last_candle['Open']:
        return -1
    return 0

def get_volatility_score(ticker):
    data = download_data(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0

    atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
    latest_atr = atr.iloc[-1]

    # Higher ATR suggests higher volatility - score accordingly
    if latest_atr > 0.02 * data['Close'].iloc[-1]:  # example threshold
        return 1
    return 0
