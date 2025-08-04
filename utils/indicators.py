import yfinance as yf
import numpy as np
import ta

def get_ticker(asset):
    mapping = {
        "Gold": "GC=F",
        "EURUSD": "EURUSD=X",
        "USDJPY": "JPY=X",
    }
    return mapping.get(asset, "")

def get_rsi_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty or len(data) < 14:
        return 0

    close = data['Close'].squeeze()
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
    latest_rsi = rsi.iloc[-1].item()

    return 1 if latest_rsi < 30 else 0

def get_macd_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty or len(data) < 26:
        return 0

    close = data['Close'].squeeze()
    macd_indicator = ta.trend.MACD(close)
    macd = macd_indicator.macd()
    signal = macd_indicator.macd_signal()

    macd_prev = macd.iloc[-2].item()
    macd_now = macd.iloc[-1].item()
    signal_prev = signal.iloc[-2].item()
    signal_now = signal.iloc[-1].item()

    if macd_prev < signal_prev and macd_now > signal_now:
        return 1
    return 0

def get_candle_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="5d", interval="1d")
    if data.empty:
        return 0

    open_ = data['Open'].iloc[-1].item()
    close = data['Close'].iloc[-1].item()
    return 1 if close > open_ else 0

def get_news_score(asset):
    print(f"Checking news impact for {asset}")
    return 1  # Stub value

def get_v_
