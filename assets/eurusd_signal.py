import yfinance as yf
from utils.indicators import get_rsi_score, get_macd_score, get_candle_score, get_volatility_score

def generate_eurusd_signal_with_score():
    ticker = "EURUSD=X"
    data = yf.download(ticker, period="1mo", interval="1h", auto_adjust=True)

    rsi_score = get_rsi_score(data, period=14)
    macd_score = get_macd_score(data)
    candle_score = get_candle_score(data)
    volatility_score = get_volatility_score(data)

    total_score = rsi_score + macd_score + candle_score + volatility_score

    if total_score >= 3:
        signal = "Buy"
    elif total_score <= -3:
        signal = "Sell"
    else:
        signal = "Hold"

    return {
        "signal": signal,
        "scores": {
            "RSI": rsi_score,
            "MACD": macd_score,
            "Candle": candle_score,
            "Volatility": volatility_score,
        },
        "total_score": total_score,
    }
