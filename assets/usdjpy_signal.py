# assets/usdjpy_signal.py
from utils.indicators import get_rsi_score, get_macd_score, get_candle_score, get_volatility_score
from utils.volatility import get_risk_reward_ratio
from ml_model import get_ml_confidence

def generate_usdjpy_signal():
    ticker = "JPY=X"
    rsi_score = get_rsi_score(ticker)
    macd_score = get_macd_score(ticker)
    candle_score = get_candle_score(ticker)
    volatility_score = get_volatility_score(ticker)

    total_score = rsi_score + macd_score + candle_score + volatility_score
    base_confidence = (total_score + 4) / 8  # Normalize to 0-1

    ml_conf = get_ml_confidence(ticker)
    final_conf = (base_confidence + ml_conf) / 2

    if final_conf > 0.75:
        signal = "Buy"
    elif final_conf < 0.25:
        signal = "Sell"
    else:
        signal = "Hold"

    return {
        "ticker": ticker,
        "signal": signal,
        "final_confidence": round(final_conf, 2),
        "ml_confidence": round(ml_conf, 2),
        "base_confidence": round(base_confidence, 2),
        "risk_reward": get_risk_reward_ratio(ticker)
    }
