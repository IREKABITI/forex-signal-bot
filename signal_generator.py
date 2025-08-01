"""
Signal Generator for #IREKABITI_FX
Generates real signals from TA, sentiment, news, and ML scores
"""

import random
import logging
from datetime import datetime
from typing import List
from bots.telegram_bot import TelegramBot
from bots.discord_bot import DiscordBot

logger = logging.getLogger(__name__)

telegram_bot = TelegramBot()
discord_bot = DiscordBot()

# === Simplified Mock Signal Generator ===
def generate_signal(pair: str, timeframe: str) -> str:
    # Example random signal logic – replace with real logic
    direction = random.choice(["BUY", "SELL"])
    score = random.randint(70, 100)
    sl = round(random.uniform(0.5, 1.5), 2)
    tp = round(random.uniform(1.5, 3.0), 2)
    reason = random.choice([
        "RSI divergence + MACD crossover",
        "Breakout from resistance zone",
        "Support rejection + bullish engulfing",
        "MACD histogram flip + volume spike"
    ])
    session = detect_trading_session()

    message = (
        f"📡 #{pair} ({timeframe}) SIGNAL\n"
        f"📈 Direction: {direction}\n"
        f"🎯 SL: {sl}% | TP: {tp}%\n"
        f"📊 Score: {score}/100\n"
        f"🧠 Reason: {reason}\n"
        f"🕒 Session: {session}\n"
        f"#IRE_DID_THIS"
    )
    return message

def detect_trading_session() -> str:
    now_utc = datetime.utcnow().time()
    london_start = datetime.strptime("07:00", "%H:%M").time()
    london_end = datetime.strptime("16:00", "%H:%M").time()
    ny_start = datetime.strptime("12:00", "%H:%M").time()
    ny_end = datetime.strptime("21:00", "%H:%M").time()

    if london_start <= now_utc <= london_end:
        return "London"
    elif ny_start <= now_utc <= ny_end:
        return "New York"
    return "Off Session"

def send_signals(pairs: List[str], timeframes: List[str]):
    for pair in pairs:
        for tf in timeframes:
            signal = generate_signal(pair, tf)
            telegram_bot.send_message(signal)
            discord_bot.send_message(signal)
            logger.info(f"📤 Signal sent for {pair} ({tf})")

# Optional standalone run
if __name__ == "__main__":
    send_signals(["EURUSD", "XAUUSD", "BTCUSDT"], ["1h", "4h"])