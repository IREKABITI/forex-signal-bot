# utils/volatility.py
import yfinance as yf
import numpy as np

def get_risk_reward_ratio(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    close = data['Close'].values
    atr = yf.download(ticker, period="1mo", interval="1d")['Close'].pct_change().std()
    if atr == 0:
        return 1.0
    risk_reward = close[-1] / atr
    return round(risk_reward, 2)

def get_volatility_score(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    high = data['High'].values
    low = data['Low'].values
    close = data['Close'].values
    atr = talib.ATR(high, low, close, timeperiod=14)[-1]
    if atr > np.mean(atr):
        return -1
    return 1
