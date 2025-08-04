# assets/usdjpy_signal.py
from utils.session_filter import get_current_session
from utils.indicators import get_rsi_score, get_macd_score, get_candle_score
from utils.news_filter import get_news_score
from utils.volatility import get_volatility_score

ASSET_NAME = "USDJPY"

def generate_usdjpy_signal_with_score():
    session = get_current_session()
    if session == 'Off Hours':
        print(f"⏳ Skipping {ASSET_NAME} - Off Hours")
        return None

    rsi = get_rsi_score(ASSET_NAME)
    macd = get_macd_score(ASSET_NAME)
    candle = get_candle_score(ASSET_NAME)
    news = get_news_score(ASSET_NAME)
    session_score = 1  # session active
    volatility = get_volatility_score(ASSET_NAME)

    total_score = rsi + macd + candle + news + session_score + volatility

    if total_score >= 4:
        signal_text = "Buy Signal"
    elif total_score <= 2:
        signal_text = "Sell Signal"
    else:
        signal_text = "Hold / No Clear Signal"

    return {
        "asset": ASSET_NAME,
        "signal": signal_text,
        "score": total_score
    }
