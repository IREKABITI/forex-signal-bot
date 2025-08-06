# assets/eurusd_signal.py

import logging
from utils.indicators import get_rsi_score, get_macd_score, get_candle_score, get_volatility_score
from utils.session_filter import is_in_trading_session
from utils.news_filter import check_news_impact
from utils.volatility import calculate_risk_reward
from alert_manager import send_alerts

# Hardcoded Telegram/Discord
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

def generate_eurusd_signal_with_score():
    asset = "EURUSD"
    ticker = "EURUSD=X"

    logging.info(f"Checking news for {asset} ({ticker})")
    news_score = check_news_impact(asset)
    session_ok = is_in_trading_session()

    if not session_ok:
        logging.info(f"⏸️ Market closed, skipping {asset}")
        return None

    # Scores
    rsi = get_rsi_score(ticker)
    macd = get_macd_score(ticker)
    candle = get_candle_score(ticker)
    volatility = get_volatility_score(ticker)

    rr_ratio = calculate_risk_reward(ticker)

    scores = [rsi, macd, candle, news_score, volatility]
    total = sum(scores)
    max_score = len(scores)
    confidence = total / max_score

    if total <= 2:
        logging.info(f"❌ Signal '{asset}' rejected due to low score ({total})")
        return None

    if total >= 4:
        signal = "Buy"
        emoji = "🟢"
    elif total <= -4:
        signal = "Sell"
        emoji = "🔴"
    else:
        signal = "Hold / No Clear Signal"
        emoji = "🟡"

    if confidence >= 0.75:
        level = "High"
    elif confidence >= 0.5:
        level = "Medium"
    else:
        level = "Low"

    alert_msg = (
        f"{emoji} {asset} {signal} Signal ({total}/{max_score} Confidence: {level})\n"
        f"📊 RSI: {rsi}, MACD: {macd}, Candle: {candle}, News: {news_score}, Volatility: {volatility}\n"
        f"🎯 Risk/Reward Ratio: {rr_ratio:.2f}\n"
        f"#IRE_DID_THIS"
    )

    logging.info(f"✅ Sending alert: {alert_msg}")
    send_alerts(alert_msg, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK)
    return {
        "signal": signal,
        "score": total,
        "confidence_level": level,
        "components": {
            "RSI": rsi, "MACD": macd, "Candle": candle, "News": news_score, "Volatility": volatility
        }
    }
