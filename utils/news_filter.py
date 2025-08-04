from utils.helpers import get_ticker

def get_news_score(asset):
    ticker = get_ticker(asset)
    print(f"Checking news for {asset} ({ticker})")
    return 1  # Placeholder stub
