# signal_generator.py
import random
from utils.indicators import calculate_rsi, calculate_macd, detect_candle_pattern, detect_trend, detect_support_resistance, check_session, check_news, check_volatility

def generate_signals(config):
    assets = config.get('assets', ['EURUSD', 'GBPUSD', 'XAUUSD'])
    signals = []

    for asset in assets:
        score = 0
        details = {}

        # Calculate indicators
        rsi = calculate_rsi(asset)
        macd = calculate_macd(asset)
        candle = detect_candle_pattern(asset)
        trend = detect_trend(asset)
        support_resistance = detect_support_resistance(asset)
        session = check_session()
        news = check_news(asset)
        volatility = check_volatility(asset)

        # Scoring logic (1 point per positive indicator)
        if rsi == 'bullish':
            score +=1
            details['RSI'] = True
        else:
            details['RSI'] = False

        if macd == 'bullish':
            score +=1
            details['MACD'] = True
        else:
            details['MACD'] = False

        if candle == 'bullish':
            score +=1
            details['Candle'] = True
        else:
            details['Candle'] = False

        if trend == 'bullish':
            score +=1
            details['Trend'] = True
        else:
            details['Trend'] = False

        if support_resistance == 'bullish':
            score +=1
            details['S/R'] = True
        else:
            details['S/R'] = False

        if session:
            score +=1
            details['Session'] = True
        else:
            details['Session'] = False

        if not news:
            score +=1
            details['News'] = True
        else:
            details['News'] = False

        if volatility:
            score +=1
            details['Volatility'] = True
        else:
            details['Volatility'] = False

        # Determine confidence level
        if score >= 6:
            confidence = 'High'
        elif score >= 3:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        # Determine signal direction (simplified example)
        direction = 'Buy' if score >= 4 else 'Sell'

        signal = {
            'asset': asset,
            'score': score,
            'confidence': confidence,
            'direction': direction,
            'details': details
        }

        signals.append(signal)

    return signals
