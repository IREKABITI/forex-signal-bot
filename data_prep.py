# data_prep.py
import yfinance as yf
import pandas as pd
import logging

def fetch_price_data(ticker, period='7d', interval='15m'):
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
        if data.empty:
            logging.warning(f"No data fetched for {ticker}")
            return None
        data.dropna(inplace=True)
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        return None

def prepare_features(data):
    try:
        data = data.copy()
        data['Return'] = data['Close'].pct_change()
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data.dropna(inplace=True)
        return data
    except Exception as e:
        logging.error(f"Error preparing features: {e}")
        return None
