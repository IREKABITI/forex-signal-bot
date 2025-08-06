import yfinance as yf
import pandas as pd
import numpy as np
import ta

def download_data(ticker, period="1mo", interval="1d"):
    """Download historical price data."""
    # auto_adjust=True by default in new yfinance versions
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    if data.empty:
        raise ValueError(f"No data for ticker {ticker}")
    return data

def get_rsi_score(ticker):
    """Calculate RSI score (0-1 scale)."""
    data = download_data(ticker)
    rsi = ta.momentum.RSIIndicator(data['Close']).rsi()
    latest_rsi = rsi.iloc[-1]

    # Score logic: RSI <30 oversold (bullish), >70 overbought (bearish)
    if latest_rsi < 30:
        return 1  # strong buy signal
    elif latest_rsi > 70:
        return 0  # strong sell signal
    else:
        return 0.5  # neutral

def get_macd_score(ticker):
    """Calculate MACD score."""
    data = download_data(ticker)
    macd = ta.trend.MACD(data['Close'])
    macd_diff = macd.macd_diff()
    latest_diff = macd_diff.iloc[-1]

    # Score logic: positive diff = bullish, negative = bearish
    if latest_diff > 0:
        return 1
    elif latest_diff < 0:
        return 0
    else:
        return 0.5

def get_candle_score(ticker):
    """Simple candle pattern score based on latest candle."""
    data = download_data(ticker, period="5d")
    candle = data.iloc[-1]
    open_ = candle['Open']
    close = candle['Close']

    # Bullish candle if close > open
    if close > open_:
        return 1
    elif close < open_:
        return 0
    else:
        return 0.5

def get_volatility_score(ticker):
    """Calculate volatility score based on ATR normalized."""
    data = download_data(ticker, period="1mo")
    atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
    latest_atr = atr.iloc[-1]
    avg_atr = atr.mean()

    # If current ATR higher than average => more volatile (score=1), else less (0)
    if latest_atr > avg_atr:
        return 1
    else:
        return 0.5

# Add more indicator scoring functions as needed
