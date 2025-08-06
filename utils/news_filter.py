import asyncio
import aiohttp
import logging

# Your Telegram and Discord credentials
TELEGRAM_TOKEN = "8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo"
TELEGRAM_CHAT_ID = "5689209090"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1402201260857233470/mwzakXPNjf6S_BPG4ZbK_1MmtivoO2AZKtzYFTrVtAm-68X0MW2HJ1naKCD33Hh2E8Zp"

NEWS_API_URL = "https://newsdata.io/api/1/news"

async def fetch_news(ticker, session):
    params = {
        'apikey': 'your_newsdata_api_key_here',  # replace with your actual API key
        'q': ticker,
        'language': 'en',
        'category': 'business,finance',
        'page': 1
    }
    try:
        async with session.get(NEWS_API_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('results', [])
            else:
                logging.error(f"Failed to fetch news for {ticker}, status: {response.status}")
                return []
    except Exception as e:
        logging.error(f"Exception fetching news for {ticker}: {e}")
        return []

async def filter_high_impact_news(ticker):
    async with aiohttp.ClientSession() as session:
        news_items = await fetch_news(ticker, session)
        high_impact_news = []
        for item in news_items:
            impact = item.get('impact', '').lower()
            if impact in ('high', 'medium'):
                high_impact_news.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'impact': impact
                })
        return high_impact_news

def send_alert(message):
    # Placeholder for alert sending, implement Telegram and Discord alert functions here
    pass

# Example sync wrapper to use in main code (optional)
def get_high_impact_news_sync(ticker):
    return asyncio.run(filter_high_impact_news(ticker))

