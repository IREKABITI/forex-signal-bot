# utils/indicators.py
import random

def calculate_rsi(asset):
    # Dummy implementation: randomly return bullish or bearish
    return random.choice(['bullish', 'bearish'])

def calculate_macd(asset):
    # Dummy implementation
    return random.choice(['bullish', 'bearish'])

def detect_candle_pattern(asset):
    # Dummy implementation
    patterns = ['bullish', 'bearish', 'neutral']
    return random.choice(patterns)

def detect_trend(asset):
    # Dummy implementation
    return random.choice(['bullish', 'bearish'])

def detect_support_resistance(asset):
    # Dummy implementation
    return random.choice(['bullish', 'bearish'])

def check_session():
    # Dummy: assume session is always open
    return True

def check_news(asset):
    # Dummy: randomly simulate no news or news
    return random.choice([False, True])

def check_volatility(asset):
    # Dummy: randomly simulate volatility condition
    return random.choice([True, False])
