# utils/news_filter.py

import random
import logging

def get_mock_news_impact(symbol):
    """
    Simulate news impact score and tag for a given symbol.
    In real usage, integrate NewsData.io, Alpha Vantage, or a live source.
    """
    # Simulated impact level
    impact_level = random.choice(["High", "Medium", "Low", "None"])
    
    if impact_level == "High":
        impact_score = 1.0
        tag = "🔴 High Impact News"
    elif impact_level == "Medium":
        impact_score = 0.5
        tag = "🟠 Medium Impact News"
    elif impact_level == "Low":
        impact_score = 0.2
        tag = "🟢 Low Impact News"
    else:
        impact_score = 0.0
        tag = "⚪ No Significant News"
    
    logging.info(f"📰 News Impact for {symbol}: {tag} ({impact_score})")
    return impact_score, tag

def news_filter(symbol, threshold=0.7):
    """
    Check if news impact score is acceptable.
    Reject signals if impact score exceeds threshold.
    """
    score, tag = get_mock_news_impact(symbol)
    if score > threshold:
        logging.warning(f"⚠️ News impact too high for {symbol}, rejecting signal.")
        return False, score, tag
    return True, score, tag
