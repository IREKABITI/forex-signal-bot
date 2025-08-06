import requests
import logging
import time
from cachetools import TTLCache

# Telegram and Discord credentials for alerting
TELEGRAM_TOKEN = '8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo'
TELEGRAM_CHAT_ID = '5689209090'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp'

# Simple in-memory cache for news data, expires after 1800 seconds (30 mins)
news_cache = TTLCache(maxsize=100, ttl=1800)

def fetch_news(ticker):
    """Fetch news related to ticker from NewsData.io or other API with caching."""
    if ticker in news_cache:
        logging.debug(f"News for {ticker} retrieved from cache")
        return news_cache[ticker]

    try:
        # Example: replace with your actual news API endpoint and params
        api_key = 'YOUR_NEWSDATA_IO_API_KEY'
        url = f'https://newsdata.io/api/1/news?apikey={api_key}&q={ticker}&language=en'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news_data = response.json()
        # Process and filter news as needed
        news_cache[ticker] = news_data
        logging.info(f"Fetched news for {ticker}, total articles: {len(news_data.get('results', []))}")
        return news_data
    except Exception as e:
        logging.error(f"Error fetching news for {ticker}: {e}")
        return None

def evaluate_news_impact(news_data):
    """Analyze news articles and assign impact score: 0 (low), 1 (medium), 2 (high)."""
    if not news_data or 'results' not in news_data:
        return 0

    impact_score = 0
    for article in
