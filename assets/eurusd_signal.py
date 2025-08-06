# assets/eurusd_signal.py

import logging
from utils.indicators import get_rsi_score, get_macd_score, get_candle_score, get_volatility_score
from alert_manager import send_alerts

# Your Telegram and Discord credentials (hardcoded)
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

def generate_eurusd_signal_with_score(data):
    """
    Generate EURUSD trading signal with confidence scoring.
    Input:
        data - price data DataFrame for EURUSD
    Returns:
        dict with signal info and score breakdown
    """

    # Calculate indicator scores
    rsi_score = get_rsi_score(data, period=14)
    macd_score = get_macd_score(data)
    candle_score = get_candle_score(data)
    volatility_score = get_volatility_score(data)

    # Combine scores - max 6 points total as example
    total_score = rsi_score + macd_score + candle_score + volatility_score

    # Determine confidence level text
    if total_score >= 5:
        confidence = "High"
    elif total_score >= 3:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Determine buy/sell/hold based on score and conditions
    if total_score >= 4:
        signal = "Buy" if rsi_score + macd_score > candle_score else "Sell"
    else:
        signal = "Hold"

    signal_data = {
        "asset": "EURUSD",
        "signal": signal,
        "score": total_score,
        "confidence": confidence,
        "details": {
            "RSI": rsi_score,
            "MACD": macd_score,
            "Candle": candle_score,
            "Volatility": volatility_score,
        }
    }

    # Prepare alert message
    emoji = "🟢" if signal == "Buy" else "🔴" if signal == "Sell" else "⚪️"
    alert_msg = (
        f"{emoji} EURUSD {signal} Signal ({total_score}/6 Confidence: {confidence})\n"
        f"Score Breakdown: RSI({rsi_score}), MACD({macd_score}), Candle({candle_score}), Volatility({volatility_score})"
    )

    # Send alerts
    try:
        send_alerts(alert_msg, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK)
        logging.info(f"✅ Sent alert: {alert_msg}")
    except Exception as e:
        logging.error(f"❌ Failed to send alert: {e}")

    return signal_data
