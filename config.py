"""
Configuration management for #IREKABITI_FX
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
import pytz

@dataclass
class TradingSession:
    """Trading session configuration"""
    name: str
    start_hour: int
    end_hour: int
    timezone: str

class Config:
    """Central configuration management"""
    
    def __init__(self):
        # Bot Tokens
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
        
        # API Keys for Market Data
        self.ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
        self.BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
        self.NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
        
        # Social Media APIs
        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
        self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
        self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
        
        # MetaTrader Configuration
        self.MT5_LOGIN = os.getenv("MT5_LOGIN")
        self.MT5_PASSWORD = os.getenv("MT5_PASSWORD")
        self.MT5_SERVER = os.getenv("MT5_SERVER", "MetaQuotes-Demo")
        
        # Application Settings
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.TIMEZONE = os.getenv("TIMEZONE", "UTC")
        
        # Database
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///irekabi_fx.db")
        
        # Trading Configuration
        self.SUPPORTED_FOREX_PAIRS = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
            "AUDUSD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"
        ]
        
        self.SUPPORTED_CRYPTO_PAIRS = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT",
            "XRPUSDT", "LTCUSDT", "LINKUSDT", "BCHUSDT", "XLMUSDT"
        ]
        
        self.TIMEFRAMES = ["5m", "15m", "1h", "4h"]
        
        # Trading Sessions (London & New York only)
        self.TRADING_SESSIONS = [
            TradingSession("London", 8, 17, "Europe/London"),
            TradingSession("New York", 13, 22, "America/New_York")
        ]
        
        # Signal Configuration
        self.MIN_SIGNAL_CONFIDENCE = 70
        self.MAX_DAILY_SIGNALS = 10
        self.SIGNAL_COOLDOWN_MINUTES = 30
        
        # Risk Management
        self.DEFAULT_RISK_PERCENTAGE = 2.0
        self.MAX_RISK_PERCENTAGE = 5.0
        self.ATR_MULTIPLIER = 2.0
        
        # ML Model Configuration
        self.ML_MODEL_UPDATE_INTERVAL = 24  # hours
        self.SENTIMENT_WEIGHT = 0.3
        self.TECHNICAL_WEIGHT = 0.7
        
        # Notification Settings
        self.DAILY_REPORT_TIME = "22:00"
        self.WEEKLY_REPORT_DAY = "Sunday"
        
        # Admin Users (Telegram/Discord IDs)
        self.ADMIN_USERS = self._parse_admin_users()
        
        # File Paths
        self.DATA_DIR = os.getenv("DATA_DIR", "./data")
        self.LOGS_DIR = os.getenv("LOGS_DIR", "./logs")
        self.MODELS_DIR = os.getenv("MODELS_DIR", "./models")
        
        # Ensure directories exist
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.MODELS_DIR, exist_ok=True)
    
    def _parse_admin_users(self) -> List[str]:
        """Parse admin users from environment variable"""
        admin_str = os.getenv("ADMIN_USERS", "")
        return [user.strip() for user in admin_str.split(",") if user.strip()]
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        return str(user_id) in self.ADMIN_USERS
    
    def is_trading_session_active(self) -> bool:
        """Check if any trading session is currently active"""
        from datetime import datetime
        import pytz
        
        current_utc = datetime.now(pytz.UTC)
        
        for session in self.TRADING_SESSIONS:
            session_tz = pytz.timezone(session.timezone)
            session_time = current_utc.astimezone(session_tz)
            
            if session.start_hour <= session_time.hour < session.end_hour:
                return True
        
        return False
    
    def get_active_trading_session(self) -> str:
        """Get the name of the currently active trading session"""
        from datetime import datetime
        import pytz
        
        current_utc = datetime.now(pytz.UTC)
        
        for session in self.TRADING_SESSIONS:
            session_tz = pytz.timezone(session.timezone)
            session_time = current_utc.astimezone(session_tz)
            
            if session.start_hour <= session_time.hour < session.end_hour:
                return session.name
        
        return "Closed"
    
    @property
    def all_supported_pairs(self) -> List[str]:
        """Get all supported trading pairs"""
        return self.SUPPORTED_FOREX_PAIRS + self.SUPPORTED_CRYPTO_PAIRS
    
    def get_pair_type(self, pair: str) -> str:
        """Determine if pair is forex or crypto"""
        if pair in self.SUPPORTED_FOREX_PAIRS:
            return "forex"
        elif pair in self.SUPPORTED_CRYPTO_PAIRS:
            return "crypto"
        else:
            return "unknown"

# Global config instance
config = Config()
