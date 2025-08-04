import yfinance as yf
import talib
import numpy as np

def get_rsi_score(asset):
    # Fetch historical data for asset (assuming asset ticker for Yahoo Finance)
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0
    close = data['Close'].values
    rsi = talib.RSI(close, timeperiod=14)
    latest_rsi = rsi[-1]
    # Score 1 if RSI < 30 (oversold), else 0
    return 1 if latest_rsi < 30 else 0

def get_macd_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0
    close = data['Close'].values
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    # Score 1 if MACD crosses above signal line (bullish)
    if macd[-2] < signal[-2] and macd[-1] > signal[-1]:
        return 1
    return 0

def get_candle_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="5d", interval="1d")
    if data.empty:
        return 0
    open_ = data['Open'].values[-1]
    close = data['Close'].values[-1]
    # Bullish candle (close > open)
    return 1 if close > open_ else 0

def get_news_score(asset):
    # Placeholder: integrate with real news API or sentiment analysis
    # For now, always return 1 (neutral/good)
    return 1

def get_volatility_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty:
        return 0
    high = data['High'].values
    low = data['Low'].values
    close = data['Close'].values
    # Calculate average true range (ATR)
    tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1]))
    atr = np.mean(tr)
    # Score 1 if ATR is above threshold (indicating volatility)
    threshold = 0.5  # Adjust per asset scale
    return 1 if atr > threshold else 0

def get_ticker(asset):
    # Map asset names to Yahoo Finance tickers
    mapping = {
        "Gold": "GC=F",
        "EURUSD": "EURUSD=X",
        "USDJPY": "JPY=X",
    }
    return mapping.get(asset, "")
