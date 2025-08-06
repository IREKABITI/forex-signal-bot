# utils/helpers.py

import datetime as dt
import pytz

def format_percentage(value):
    """Format float as percentage string with 2 decimals."""
    return f"{value:.2%}"

def get_current_utc_time():
    """Return current UTC time."""
    return dt.datetime.now(dt.timezone.utc)

def get_local_time(timezone_str="US/Eastern"):
    """Return local time in specified timezone."""
    tz = pytz.timezone(timezone_str)
    return dt.datetime.now(tz)

def get_trading_session():
    """Detect current trading session."""
    utc_now = get_current_utc_time().time()
    if dt.time(6, 0) <= utc_now < dt.time(14, 0):
        return "London"
    elif dt.time(13, 0) <= utc_now < dt.time(21, 0):
        return "New York"
    else:
        return "Off-session"

def is_trading_day():
    """Check if today is a weekday (trading day)."""
    return dt.datetime.utcnow().weekday() < 5

def calculate_pips(open_price, close_price, pair="USDJPY"):
    """Calculate pips for a forex trade."""
    pip_factor = 100.0 if "JPY" in pair else 10000.0
    return (close_price - open_price) * pip_factor
