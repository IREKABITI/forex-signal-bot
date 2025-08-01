"""
Validation utilities for #IREKABITI_FX
Input validation and data sanitization
"""

import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from decimal import Decimal, InvalidOperation

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    try:
        if not isinstance(symbol, str):
            return False
            
        symbol = symbol.upper().strip()
        
        # Check if symbol is in supported lists
        all_symbols = settings.TRADING_PAIRS_FOREX + settings.TRADING_PAIRS_CRYPTO
        
        return symbol in all_symbols
        
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {e}")
        return False

def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe format"""
    try:
        if not isinstance(timeframe, str):
            return False
            
        return timeframe.lower() in [tf.lower() for tf in settings.TIMEFRAMES]
        
    except Exception as e:
        logger.error(f"Error validating timeframe {timeframe}: {e}")
        return False

def validate_price(price: Union[str, float, int]) -> bool:
    """Validate price value"""
    try:
        if price is None:
            return False
            
        # Convert to float
        price_float = float(price)
        
        # Check if positive
        if price_float <= 0:
            return False
            
        # Check reasonable bounds (not too small or too large)
        if price_float < 0.000001 or price_float > 1000000:
            return False
            
        return True
        
    except (ValueError, TypeError, OverflowError):
        return False

def validate_confidence(confidence: Union[str, int, float]) -> bool:
    """Validate confidence score (0-100)"""
    try:
        conf_int = int(confidence)
        return 0 <= conf_int <= 100
        
    except (ValueError, TypeError):
        return False

def validate_risk_percent(risk_percent: Union[str, float, int]) -> bool:
    """Validate risk percentage (0-10)"""
    try:
        risk_float = float(risk_percent)
        return 0 <= risk_float <= 10
        
    except (ValueError, TypeError):
        return False

def validate_direction(direction: str) -> bool:
    """Validate trading direction"""
    try:
        if not isinstance(direction, str):
            return False
            
        return direction.upper() in ['BUY', 'SELL', 'HOLD']
        
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    try:
        if not isinstance(email, str):
            return False
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    except Exception:
        return False

def validate_user_id(user_id: Union[str, int]) -> bool:
    """Validate user ID format"""
    try:
        # Convert to string and check if it's numeric
        user_str = str(user_id).strip()
        
        # Check if it's a valid positive integer
        return user_str.isdigit() and int(user_str) > 0
        
    except Exception:
        return False

def validate_json_data(data: str) -> bool:
    """Validate JSON string"""
    try:
        import json
        json.loads(data)
        return True
        
    except (json.JSONDecodeError, TypeError):
        return False

def validate_datetime_string(dt_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """Validate datetime string format"""
    try:
        datetime.strptime(dt_string, format_string)
        return True
        
    except (ValueError, TypeError):
        return False

def sanitize_string(input_string: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Sanitize string input"""
    try:
        if not isinstance(input_string, str):
            return ""
            
        # Remove leading/trailing whitespace
        sanitized = input_string.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            
        # Remove HTML tags if not allowed
        if not allow_html:
            import re
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
            
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Error sanitizing string: {e}")
        return ""

def validate_signal_data(signal_data: Dict[str, Any]) -> List[str]:
    """Validate complete trading signal data"""
    errors = []
    
    try:
        # Required fields
        required_fields = [
            'symbol', 'direction', 'entry_price', 'tp_price', 
            'sl_price', 'confidence', 'timeframe'
        ]
        
        for field in required_fields:
            if field not in signal_data:
                errors.append(f"Missing required field: {field}")
                
        # Validate individual fields
        if 'symbol' in signal_data and not validate_symbol(signal_data['symbol']):
            errors.append("Invalid symbol")
            
        if 'direction' in signal_data and not validate_direction(signal_data['direction']):
            errors.append("Invalid direction")
            
        if 'entry_price' in signal_data and not validate_price(signal_data['entry_price']):
            errors.append("Invalid entry price")
            
        if 'tp_price' in signal_data and not validate_price(signal_data['tp_price']):
            errors.append("Invalid take profit price")
            
        if 'sl_price' in signal_data and not validate_price(signal_data['sl_price']):
            errors.append("Invalid stop loss price")
            
        if 'confidence' in signal_data and not validate_confidence(signal_data['confidence']):
            errors.append("Invalid confidence score")
            
        if 'timeframe' in signal_data and not validate_timeframe(signal_data['timeframe']):
            errors.append("Invalid timeframe")
            
        if 'risk_percent' in signal_data and not validate_risk_percent(signal_data['risk_percent']):
            errors.append("Invalid risk percentage")
            
        # Validate price relationships
        if all(field in signal_data for field in ['entry_price', 'tp_price', 'sl_price', 'direction']):
            entry = float(signal_data['entry_price'])
            tp = float(signal_data['tp_price'])
            sl = float(signal_data['sl_price'])
            direction = signal_data['direction'].upper()
            
            if direction == 'BUY':
                if tp <= entry:
                    errors.append("Take profit must be above entry price for BUY signal")
                if sl >= entry:
                    errors.append("Stop loss must be below entry price for BUY signal")
            elif direction == 'SELL':
                if tp >= entry:
                    errors.append("Take profit must be below entry price for SELL signal")
                if sl <= entry:
                    errors.append("Stop loss must be above entry price for SELL signal")
                    
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        
    return errors

def validate_portfolio_data(portfolio_data: Dict[str, Any]) -> List[str]:
    """Validate portfolio optimization data"""
    errors = []
    
    try:
        # Check if symbols are provided
        if 'symbols' in portfolio_data:
            symbols = portfolio_data['symbols']
            if not isinstance(symbols, list):
                errors.append("Symbols must be a list")
            else:
                for symbol in symbols:
                    if not validate_symbol(symbol):
                        errors.append(f"Invalid symbol: {symbol}")
                        
        # Check weights if provided
        if 'weights' in portfolio_data:
            weights = portfolio_data['weights']
            if not isinstance(weights, dict):
                errors.append("Weights must be a dictionary")
            else:
                total_weight = sum(weights.values())
                if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
                    errors.append(f"Weights must sum to 1.0, got {total_weight}")
                    
                for symbol, weight in weights.items():
                    if not validate_symbol(symbol):
                        errors.append(f"Invalid symbol in weights: {symbol}")
                    if not 0 <= weight <= 1:
                        errors.append(f"Weight for {symbol} must be between 0 and 1")
                        
    except Exception as e:
        errors.append(f"Portfolio validation error: {str(e)}")
        
    return errors

def validate_api_request(request_data: Dict[str, Any], endpoint: str) -> List[str]:
    """Validate API request data based on endpoint"""
    errors = []
    
    try:
        if endpoint == "generate_signal":
            if 'symbol' not in request_data:
                errors.append("Symbol is required")
            elif not validate_symbol(request_data['symbol']):
                errors.append("Invalid symbol")
                
            if 'timeframe' in request_data and not validate_timeframe(request_data['timeframe']):
                errors.append("Invalid timeframe")
                
        elif endpoint == "optimize_portfolio":
            errors.extend(validate_portfolio_data(request_data))
            
        elif endpoint == "backtest":
            if 'days' in request_data:
                try:
                    days = int(request_data['days'])
                    if not 1 <= days <= 365:
                        errors.append("Days must be between 1 and 365")
                except (ValueError, TypeError):
                    errors.append("Days must be a valid integer")
                    
        elif endpoint == "get_prices":
            if 'symbols' not in request_data:
                errors.append("Symbols parameter is required")
            else:
                symbols = request_data['symbols'].split(',')
                for symbol in symbols:
                    if not validate_symbol(symbol.strip()):
                        errors.append(f"Invalid symbol: {symbol}")
                        
    except Exception as e:
        errors.append(f"API validation error: {str(e)}")
        
    return errors

def validate_notification_settings(settings_data: Dict[str, Any]) -> List[str]:
    """Validate notification settings"""
    errors = []
    
    try:
        if 'push_notifications' in settings_data:
            if not isinstance(settings_data['push_notifications'], bool):
                errors.append("push_notifications must be boolean")
                
        if 'email_notifications' in settings_data:
            if not isinstance(settings_data['email_notifications'], bool):
                errors.append("email_notifications must be boolean")
                
        if 'min_confidence' in settings_data:
            if not validate_confidence(settings_data['min_confidence']):
                errors.append("min_confidence must be between 0 and 100")
                
        if 'email' in settings_data:
            if not validate_email(settings_data['email']):
                errors.append("Invalid email format")
                
    except Exception as e:
        errors.append(f"Notification settings validation error: {str(e)}")
        
    return errors

class DataValidator:
    """Class-based validator for complex validation scenarios"""
    
    def __init__(self):
        self.errors = []
        
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        
    def clear_errors(self):
        """Clear all validation errors"""
        self.errors = []
        
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
        
    def get_errors(self) -> List[str]:
        """Get all validation errors"""
        return self.errors.copy()
        
    def validate_and_clean_signal(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean signal data"""
        self.clear_errors()
        
        # Validate required fields
        validation_errors = validate_signal_data(raw_data)
        self.errors.extend(validation_errors)
        
        if self.has_errors():
            return None
            
        # Clean and format data
        cleaned_data = {
            'symbol': raw_data['symbol'].upper().strip(),
            'direction': raw_data['direction'].upper().strip(),
            'entry_price': round(float(raw_data['entry_price']), 6),
            'tp_price': round(float(raw_data['tp_price']), 6),
            'sl_price': round(float(raw_data['sl_price']), 6),
            'confidence': int(raw_data['confidence']),
            'timeframe': raw_data['timeframe'].lower().strip(),
            'risk_percent': round(float(raw_data.get('risk_percent', 2.0)), 2),
            'analysis': sanitize_string(raw_data.get('analysis', ''), max_length=500)
        }
        
        return cleaned_data
        
    def validate_market_data(self, symbol: str, timeframe: str, data: Any) -> bool:
        """Validate market data"""
        self.clear_errors()
        
        if not validate_symbol(symbol):
            self.add_error("Invalid symbol")
            
        if not validate_timeframe(timeframe):
            self.add_error("Invalid timeframe")
            
        if data is None:
            self.add_error("No market data provided")
            return False
            
        # Check if data is a pandas DataFrame with required columns
        try:
            import pandas as pd
            
            if not isinstance(data, pd.DataFrame):
                self.add_error("Market data must be a pandas DataFrame")
                return False
                
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                self.add_error(f"Missing columns: {missing_columns}")
                return False
                
            # Check for sufficient data
            if len(data) < 20:
                self.add_error("Insufficient market data (minimum 20 periods required)")
                return False
                
            # Check for NaN values
            if data[required_columns].isnull().any().any():
                self.add_error("Market data contains NaN values")
                return False
                
        except ImportError:
            self.add_error("Pandas not available for data validation")
            return False
        except Exception as e:
            self.add_error(f"Error validating market data: {str(e)}")
            return False
            
        return not self.has_errors()

# Create global validator instance
validator = DataValidator()
