import yfinance as yf
import numpy as np
from utils.helpers import get_ticker

def get_volatility_score(asset):
    ticker = get_ticker(asset)
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty or len(data) < 2:
        return 0

    high = data['High']
    low = data['Low']
    close = data['Close']

    tr = np.maximum.reduce([
        high[1:].values - low[1:].values,
        np.abs(high[1:].values - close[:-1].values),
        np.abs(low[1:].values - close[:-1].values)
    ])

    atr = np.mean(tr)
    threshold = 0.5
    return 1 if atr > threshold else 0
