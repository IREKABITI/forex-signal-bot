"""
Hardcoded configuration settings for #IREKABITI_FX
"""

from dataclasses import dataclass
from typing import List

@dataclass
class Settings:
    """Application settings"""

    # Bot Tokens
    TELEGRAM_TOKEN: str = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
    DISCORD_TOKEN: str = "YOUR_DISCORD_BOT_TOKEN"

    # API Keys
    ALPHA_VANTAGE_API_KEY: str = "YOUR_ALPHA_VANTAGE_KEY"
    BINANCE_API_KEY: str = "YOUR_BINANCE_API_KEY"
    BINANCE_SECRET_KEY: str = "YOUR_BINANCE_SECRET_KEY"
    NEWS_API_KEY: str = "pub_814ab6ff43344e0ca02a0d9746b29be2"
    TWITTER_API_KEY: str = "YOUR_TWITTER_API_KEY"
    TWITTER_API_SECRET: str = "YOUR_TWITTER_API_SECRET"
    TWITTER_ACCESS_TOKEN: str = "YOUR_TWITTER_ACCESS_TOKEN"
    TWITTER_ACCESS_TOKEN_SECRET: str = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"

    # MetaTrader Settings
    MT5_LOGIN: int = 12345678
    MT5_PASSWORD: str = "YOUR_MT5_PASSWORD"
    MT5_SERVER: str = "YOUR_MT5_SERVER"

    # Trading Settings
    TRADING_PAIRS_FOREX: List[str] = None
    TRADING_PAIRS_CRYPTO: List[str] = None
    TIMEFRAMES: List[str] = None

    # Risk Management
    MAX_RISK_PERCENT: float = 2.0
    MIN_SIGNAL_SCORE: int = 70
    MAX_DAILY_SIGNALS: int = 10

    # Session Times (UTC)
    LONDON_SESSION_START: str = "07:00"
    LONDON_SESSION_END: str = "16:00"
    NEW_YORK_SESSION_START: str = "12:00"
    NEW_YORK_SESSION_END: str = "21:00"

    # Admin Users
    ADMIN_TELEGRAM_IDS: List[int] = [5689209090]
    ADMIN_DISCORD_IDS: List[int] = [123456789012345678]

    # Database
    DATABASE_URL: str = "sqlite:///irekabiti_fx.db"

    # Scheduler
    DAILY_REPORT_TIME: str = "22:00"
    SIGNAL_CHECK_INTERVAL: int = 300  # every 5 minutes

    def __post_init__(self):
        if self.TRADING_PAIRS_FOREX is None:
            self.TRADING_PAIRS_FOREX = [
                "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
                "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"
            ]

        if self.TRADING_PAIRS_CRYPTO is None:
            self.TRADING_PAIRS_CRYPTO = [
                "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT",
                "BNBUSDT", "SOLUSDT", "XRPUSDT", "AVAXUSDT", "MATICUSDT"
            ]

        if self.TIMEFRAMES is None:
            self.TIMEFRAMES = ["5m", "15m", "1h", "4h"]

# Global settings instance
settings = Settings()