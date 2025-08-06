import yfinance as yf
import pandas as pd
import numpy as np
import ta
import logging

# Your Telegram and Discord credentials
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

def download_data(ticker, period="1mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
        if data.empty:
            logging.warning(f"No data returned for {ticker}")
        return data
    except Exception as e:
        logging.error(f"Error downloading data for {ticker}: {e}")
        return pd.DataFrame()

def get_rsi_score(ticker):
    data = download_data(ticker)
    if data.empty:
        return 0
    rsi = ta.momentum.RSIIndicator(close=data['Close']).rsi()
    last_rsi = rsi.iloc[-1]
    score = 0
    if last_rsi < 30:
        score = 1  # Oversold
    elif last_rsi > 70:
        score = -1  # Overbought
    return score

def get_macd_score(ticker):
    data = download_data(ticker)
    if data.empty:
        return 0
    macd = ta.trend.MACD(close=data['Close'])
    macd_diff = macd.macd_diff()
    last_diff = macd_diff.iloc[-1]
    if last_diff > 0:
        return 1  # Bullish
    elif last_diff < 0:
        return -1  # Bearish
    return 0

def get_candle_score(ticker):
    data = download_data(ticker, period="5d")
    if data.empty or len(data) < 2:
        return 0
    # Simple candle pattern example: Bullish Engulfing
    prev_open = data['Open'].iloc[-2]
    prev_close = data['Close'].iloc[-2]
    curr_open = data['Open'].iloc[-1]
    curr_close = data['Close'].iloc[-1]

    if (curr_open < curr_close and
        prev_open > prev_close and
        curr_open < prev_close and
        curr_close > prev_open):
        return 1  # Bullish Engulfing
    return 0

def get_volatility_score(ticker):
    data = download_data(ticker)
    if data.empty:
        return 0
    atr = ta.volatility.AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close']).average_true_range()
    last_atr = atr.iloc[-1]
    mean_atr = atr.mean()
    if last_atr > mean_atr:
        return 1  # High volatility
    return 0

# Add other indicator functions here as needed...
