# utils/volatility.py

import yfinance as yf
import numpy as np
import logging

def get_atr(ticker, period=14):
    """
    Calculate Average True Range (ATR) for given ticker.
    ATR is a measure of volatility.
    """
    try:
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        high = data['High']
        low = data['Low']
        close = data['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = np.maximum(np.maximum(tr1, tr2), tr3)
        atr = tr.rolling(window=period).mean().iloc[-1]
        logging.info(f"📊 ATR({period}) for {ticker}: {atr}")
        return atr
    except Exception as e:
        logging.error(f"❌ Failed to calculate ATR for {ticker}: {e}")
        return None

def get_volatility_score(ticker):
    """
    Returns a volatility score (1 to 3):
    1 = Low Volatility
    2 = Medium Volatility
    3 = High Volatility
    """
    atr = get_atr(ticker)
    if atr is None:
        return 1  # Default low if error

    # These thresholds can be tuned per asset class
    if atr < 0.5:
        score = 1
    elif atr < 1.5:
        score = 2
    else:
        score = 3

    logging.info(f"⚡ Volatility score for {ticker}: {score}")
    return score

def calculate_risk_reward(entry_price, stop_loss, take_profit):
    """
    Calculate risk/reward ratio given entry, stop loss and take profit.
    Returns ratio and classification emoji.
    """
    try:
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        if risk == 0:
            logging.warning("⚠️ Risk is zero, invalid stop loss")
            return None, "❌"

        ratio = reward / risk
        if ratio >= 2:
            emoji = "🟢"  # Good risk/reward
        elif ratio >= 1:
            emoji = "🟠"  # Acceptable risk/reward
        else:
            emoji = "🔴"  # Poor risk/reward

        logging.info(f"⚖️ Risk/Reward ratio: {ratio:.2f} {emoji}")
        return ratio, emoji
    except Exception as e:
        logging.error(f"❌ Failed to calculate risk/reward: {e}")
        return None, "❌"
