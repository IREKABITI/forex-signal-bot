import random
import asyncio
from typing import List
from datetime import datetime
from utils.logger import setup_logger
from bots.telegram_bot import TelegramBot
from bots.discord_bot import DiscordBot

logger = setup_logger()

class SignalGenerator:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.discord_bot = DiscordBot()

    def _generate_trade_reason(self) -> str:
        reasons = [
            "RSI Oversold + MACD Bullish Crossover",
            "Price broke resistance + Strong Volume",
            "Support bounce + Bullish candlestick pattern",
            "High Sentiment Score + Bullish RSI divergence",
            "Breakout from consolidation + News catalyst",
        ]
        return random.choice(reasons)

    def _generate_signal(self, symbol: str) -> dict:
        signal_type = random.choice(["BUY", "SELL"])
        entry = round(random.uniform(1.1000, 1.3000), 4)
        sl = round(entry - 0.0020 if signal_type == "BUY" else entry + 0.0020, 4)
        tp = round(entry + 0.0040 if signal_type == "BUY" else entry - 0.0040, 4)
        score = random.randint(70, 95)

        return {
            "symbol": symbol,
            "signal": signal_type,
            "entry": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "score": score,
            "reason": self._generate_trade_reason(),
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    def format_signal(self, signal: dict) -> str:
        return (
            f"📈 *{signal['symbol']}* SIGNAL\n"
            f"🔹 Type: *{signal['signal']}*\n"
            f"🎯 Entry: `{signal['entry']}`\n"
            f"🛑 Stop Loss: `{signal['stop_loss']}`\n"
            f"🏁 Take Profit: `{signal['take_profit']}`\n"
            f"📊 Score: *{signal['score']}%*\n"
            f"🧠 Reason: {signal['reason']}\n"
            f"🕒 Time: {signal['time']}\n"
            f"#IRE_DID_THIS"
        )

    async def generate_and_send_signals(self, symbols: List[str]):
        logger.info("🔍 Generating and sending trade signals...")
        for symbol in symbols:
            signal = self._generate_signal(symbol)
            message = self.format_signal(signal)

            await self.telegram_bot.send_signal(message)
            await self.discord_bot.send_signal(message)

        logger.info("✅ All signals sent")

# Manual trigger for testing
if __name__ == "__main__":
    async def test():
        generator = SignalGenerator()
        await generator.generate_and_send_signals(["EURUSD", "BTCUSDT", "XAUUSD"])

    asyncio.run(test())