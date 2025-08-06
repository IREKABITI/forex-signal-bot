import pandas_ta as ta

def get_rsi_score(data, period=14):
    if 'Close' not in data.columns or data.empty:
        return 0
    rsi_series = ta.rsi(data['Close'], length=period)
    latest_rsi = rsi_series.iloc[-1]
    if latest_rsi < 30:
        return 1
    elif latest_rsi > 70:
        return -1
    return 0

def get_macd_score(data):
    if 'Close' not in data.columns or data.empty:
        return 0
    macd = ta.macd(data['Close'])
    macd_diff = macd['MACDh_12_26_9'].iloc[-1]
    if macd_diff > 0:
        return 1
    elif macd_diff < 0:
        return -1
    return 0

def get_candle_score(data):
    if data.empty or len(data) < 2:
        return 0
    last = data.iloc[-1]
    if last['Close'] > last['Open']:
        return 1
    elif last['Close'] < last['Open']:
        return -1
    return 0

def get_volatility_score(data):
    if 'High' not in data.columns or 'Low' not in data.columns or 'Close' not in data.columns or data.empty:
        return 0
    atr = ta.atr(data['High'], data['Low'], data['Close'], length=14)
    latest_atr = atr.iloc[-1]
    if latest_atr > 0.005:
        return 1
    return 0
