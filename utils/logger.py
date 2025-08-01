"""
Logger utility for #IREKABITI_FX
Provides consistent logging across the application
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """Setup and configure logger with file and console handlers"""
    
    # Create logger
    logger_name = name or "irekabiti_fx"
    logger = logging.getLogger(logger_name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # File handler with rotation
    log_file = os.path.join(logs_dir, f"{logger_name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Error file handler
    error_log_file = os.path.join(logs_dir, f"{logger_name}_error.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    # Formatters
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    error_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Get the original formatted message
        message = super().format(record)
        
        # Add color if this is a console output (not a file)
        level_name = record.levelname
        if level_name in self.COLORS:
            color = self.COLORS[level_name]
            reset = self.COLORS['RESET']
            
            # Color the level name
            colored_level = f"{color}{level_name}{reset}"
            message = message.replace(level_name, colored_level, 1)
            
            # Add emoji based on level
            emoji_map = {
                'DEBUG': '🔍',
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '💥'
            }
            
            if level_name in emoji_map:
                message = f"{emoji_map[level_name]} {message}"
        
        return message

class TradingLogger:
    """Specialized logger for trading operations"""
    
    def __init__(self, name: str = "trading"):
        self.logger = setup_logger(f"irekabiti_fx_{name}")
        self.trade_file = os.path.join("logs", "trades.csv")
        self._init_trade_file()
        
    def _init_trade_file(self):
        """Initialize CSV file for trade logging"""
        if not os.path.exists(self.trade_file):
            with open(self.trade_file, 'w') as f:
                f.write("timestamp,symbol,direction,entry_price,tp_price,sl_price,confidence,risk_percent,result,pnl\n")
    
    def log_signal(self, signal_data: dict):
        """Log trading signal"""
        timestamp = datetime.now().isoformat()
        self.logger.info(
            f"🚨 SIGNAL: {signal_data['symbol']} {signal_data['direction']} "
            f"@ {signal_data['entry_price']} | Confidence: {signal_data['confidence']}% | "
            f"Risk: {signal_data['risk_percent']}%"
        )
        
        # Also log to CSV
        with open(self.trade_file, 'a') as f:
            f.write(
                f"{timestamp},{signal_data['symbol']},{signal_data['direction']},"
                f"{signal_data['entry_price']},{signal_data['tp_price']},{signal_data['sl_price']},"
                f"{signal_data['confidence']},{signal_data['risk_percent']},,\n"
            )
    
    def log_trade_result(self, symbol: str, result: str, pnl: float):
        """Log trade result"""
        emoji = "✅" if result == "win" else "❌" if result == "loss" else "⚪"
        self.logger.info(f"{emoji} RESULT: {symbol} - {result.upper()} | PnL: {pnl:.2f}%")
    
    def log_performance(self, stats: dict):
        """Log performance statistics"""
        self.logger.info(
            f"📊 PERFORMANCE: Win Rate: {stats.get('win_rate', 0):.1f}% | "
            f"Total Return: {stats.get('total_return', 0):.2f}% | "
            f"Signals: {stats.get('total_signals', 0)}"
        )

class APILogger:
    """Specialized logger for API operations"""
    
    def __init__(self):
        self.logger = setup_logger("irekabiti_fx_api")
        
    def log_request(self, endpoint: str, method: str, user: str = None):
        """Log API request"""
        user_info = f" | User: {user}" if user else ""
        self.logger.info(f"🌐 API: {method} {endpoint}{user_info}")
        
    def log_error(self, endpoint: str, error: str, user: str = None):
        """Log API error"""
        user_info = f" | User: {user}" if user else ""
        self.logger.error(f"🌐 API ERROR: {endpoint} - {error}{user_info}")
        
    def log_performance(self, endpoint: str, duration_ms: float):
        """Log API performance"""
        if duration_ms > 1000:  # Log slow requests
            self.logger.warning(f"🐌 SLOW API: {endpoint} took {duration_ms:.2f}ms")

class MLLogger:
    """Specialized logger for ML operations"""
    
    def __init__(self):
        self.logger = setup_logger("irekabiti_fx_ml")
        
    def log_training(self, symbol: str, accuracy: float, model_type: str):
        """Log model training"""
        self.logger.info(
            f"🤖 MODEL TRAINED: {symbol} - {model_type} | Accuracy: {accuracy:.3f}"
        )
        
    def log_prediction(self, symbol: str, prediction: int, confidence: float):
        """Log ML prediction"""
        direction = "BUY" if prediction == 1 else "SELL" if prediction == -1 else "HOLD"
        self.logger.info(
            f"🔮 PREDICTION: {symbol} - {direction} | Confidence: {confidence:.1f}%"
        )
        
    def log_feature_importance(self, symbol: str, top_features: dict):
        """Log feature importance"""
        features_str = ", ".join([f"{k}: {v:.3f}" for k, v in list(top_features.items())[:3]])
        self.logger.info(f"📈 FEATURES: {symbol} - Top: {features_str}")

class SystemLogger:
    """System-wide logger for monitoring"""
    
    def __init__(self):
        self.logger = setup_logger("irekabiti_fx_system")
        
    def log_startup(self, component: str):
        """Log component startup"""
        self.logger.info(f"🚀 STARTUP: {component} initialized successfully")
        
    def log_shutdown(self, component: str):
        """Log component shutdown"""
        self.logger.info(f"🛑 SHUTDOWN: {component} stopped gracefully")
        
    def log_error(self, component: str, error: str):
        """Log system error"""
        self.logger.error(f"💥 SYSTEM ERROR: {component} - {error}")
        
    def log_health_check(self, component: str, status: str, details: str = ""):
        """Log health check results"""
        emoji = "✅" if status == "healthy" else "❌"
        details_str = f" | {details}" if details else ""
        self.logger.info(f"{emoji} HEALTH: {component} - {status}{details_str}")
        
    def log_resource_usage(self, cpu_percent: float, memory_mb: float, disk_percent: float):
        """Log resource usage"""
        if cpu_percent > 80 or memory_mb > 1000 or disk_percent > 80:
            self.logger.warning(
                f"⚠️ RESOURCES: CPU: {cpu_percent:.1f}% | RAM: {memory_mb:.1f}MB | Disk: {disk_percent:.1f}%"
            )

# Convenience function for getting specialized loggers
def get_trading_logger() -> TradingLogger:
    """Get trading logger instance"""
    return TradingLogger()

def get_api_logger() -> APILogger:
    """Get API logger instance"""
    return APILogger()

def get_ml_logger() -> MLLogger:
    """Get ML logger instance"""
    return MLLogger()

def get_system_logger() -> SystemLogger:
    """Get system logger instance"""
    return SystemLogger()

# Global logger instance
logger = setup_logger()
