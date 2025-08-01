"""
News Service for #IREKABITI_FX
Fetches and analyzes financial news impact
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.settings import settings
from services.sentiment_analysis import SentimentAnalysis
from utils.logger import setup_logger

logger = setup_logger()

class NewsService:
    def __init__(self):
        self.session = None
        self.sentiment_analyzer = SentimentAnalysis()
        self.news_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def fetch_newsdata_io(self, symbols: List[str] = None, count: int = 50) -> List[Dict]:
        """Fetch news from NewsData.io API"""
        try:
            if not settings.NEWS_API_KEY:
                logger.warning("NewsData.io API key not configured")
                return []
                
            session = await self.get_session()
            
            # Create search query
            if symbols:
                query = " OR ".join([f"{symbol} forex" for symbol in symbols[:5]])  # Limit query length
            else:
                query = "forex OR cryptocurrency OR trading OR economy"
                
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": settings.NEWS_API_KEY,
                "q": query,
                "language": "en",
                "category": "business",
                "size": min(count, 50)  # API limit
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        articles = []
                        for article in data.get("results", []):
                            articles.append({
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "content": article.get("content", ""),
                                "source": article.get("source_id", ""),
                                "published_at": article.get("pubDate", ""),
                                "url": article.get("link", ""),
                                "category": article.get("category", [""])[0] if article.get("category") else "",
                                "keywords": article.get("keywords", [])
                            })
                        return articles
                    else:
                        logger.error(f"NewsData.io API error: {data.get('message', 'Unknown error')}")
                        
                else:
                    logger.error(f"NewsData.io API request failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching news from NewsData.io: {e}")
            
        return []
        
    async def fetch_alpha_vantage_news(self, symbols: List[str] = None) -> List[Dict]:
        """Fetch news from Alpha Vantage API"""
        try:
            if not settings.ALPHA_VANTAGE_API_KEY:
                return []
                
            session = await self.get_session()
            
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
                "limit": 50
            }
            
            # Add symbols if provided
            if symbols:
                params["tickers"] = ",".join(symbols[:10])  # Limit to avoid URL length issues
                
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "feed" in data:
                        articles = []
                        for article in data["feed"]:
                            articles.append({
                                "title": article.get("title", ""),
                                "description": article.get("summary", ""),
                                "content": article.get("summary", ""),
                                "source": article.get("source", ""),
                                "published_at": article.get("time_published", ""),
                                "url": article.get("url", ""),
                                "sentiment_score": float(article.get("overall_sentiment_score", 0)),
                                "sentiment_label": article.get("overall_sentiment_label", "Neutral"),
                                "ticker_sentiment": article.get("ticker_sentiment", [])
                            })
                        return articles
                        
        except Exception as e:
            logger.error(f"Error fetching news from Alpha Vantage: {e}")
            
        return []
        
    async def analyze_news_impact(self, articles: List[Dict], symbols: List[str] = None) -> Dict[str, any]:
        """Analyze news impact on market sentiment"""
        try:
            if not articles:
                return {
                    "overall_sentiment": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "high_impact_news": [],
                    "symbol_impact": {},
                    "news_summary": "No recent news available"
                }
                
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            sentiment_scores = []
            high_impact_news = []
            symbol_impact = {symbol: [] for symbol in (symbols or [])}
            
            for article in articles:
                # Analyze sentiment if not already provided
                if "sentiment_score" not in article:
                    text = f"{article['title']} {article['description']}"
                    sentiment = await self.sentiment_analyzer.analyze_text_sentiment(text)
                    sentiment_score = sentiment['positive'] - sentiment['negative']
                    article['sentiment_score'] = sentiment_score
                else:
                    sentiment_score = article['sentiment_score']
                    
                sentiment_scores.append(sentiment_score)
                
                # Categorize sentiment
                if sentiment_score > 0.2:
                    positive_count += 1
                elif sentiment_score < -0.2:
                    negative_count += 1
                else:
                    neutral_count += 1
                    
                # Check for high impact news
                impact_keywords = [
                    "federal reserve", "interest rate", "inflation", "gdp", "unemployment",
                    "central bank", "monetary policy", "economic data", "recession",
                    "crisis", "emergency", "meeting", "announcement", "decision"
                ]
                
                text_lower = f"{article['title']} {article['description']}".lower()
                if any(keyword in text_lower for keyword in impact_keywords):
                    high_impact_news.append({
                        "title": article['title'],
                        "sentiment_score": sentiment_score,
                        "published_at": article['published_at'],
                        "url": article['url']
                    })
                    
                # Check symbol-specific impact
                if symbols:
                    for symbol in symbols:
                        if symbol.lower() in text_lower:
                            symbol_impact[symbol].append({
                                "title": article['title'],
                                "sentiment_score": sentiment_score,
                                "published_at": article['published_at']
                            })
                            
            # Calculate overall sentiment
            overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # Generate summary
            news_summary = self._generate_news_summary(
                overall_sentiment, positive_count, negative_count, len(high_impact_news)
            )
            
            return {
                "overall_sentiment": overall_sentiment,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "total_articles": len(articles),
                "high_impact_news": high_impact_news[:5],  # Top 5
                "symbol_impact": symbol_impact,
                "news_summary": news_summary,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {e}")
            return {
                "overall_sentiment": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "high_impact_news": [],
                "symbol_impact": {},
                "news_summary": "Error analyzing news impact"
            }
            
    def _generate_news_summary(self, sentiment: float, positive: int, negative: int, high_impact: int) -> str:
        """Generate human-readable news summary"""
        if high_impact > 3:
            impact_text = f"🚨 {high_impact} high-impact economic news detected"
        elif high_impact > 0:
            impact_text = f"⚠️ {high_impact} notable economic events"
        else:
            impact_text = "📰 Regular market news flow"
            
        if sentiment > 0.3:
            sentiment_text = "📈 Strongly positive news sentiment"
        elif sentiment > 0.1:
            sentiment_text = "🟢 Mildly positive news sentiment"
        elif sentiment > -0.1:
            sentiment_text = "⚪ Neutral news sentiment"
        elif sentiment > -0.3:
            sentiment_text = "🟡 Mildly negative news sentiment"
        else:
            sentiment_text = "📉 Strongly negative news sentiment"
            
        return f"{impact_text} - {sentiment_text} ({positive}+ / {negative}-)"
        
    async def get_economic_calendar(self) -> List[Dict]:
        """Get economic calendar events (simplified implementation)"""
        try:
            # This would typically connect to an economic calendar API
            # For now, return a basic structure
            return [
                {
                    "event": "Interest Rate Decision",
                    "country": "USD",
                    "impact": "High",
                    "time": datetime.now() + timedelta(hours=2),
                    "forecast": "5.25%",
                    "previous": "5.25%"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []
            
    async def get_cached_news(self, symbols: List[str] = None) -> Dict[str, any]:
        """Get cached news or fetch new if expired"""
        try:
            cache_key = "_".join(sorted(symbols or ["general"]))
            current_time = datetime.now()
            
            # Check cache
            if cache_key in self.news_cache:
                cached_data = self.news_cache[cache_key]
                if (current_time - cached_data["timestamp"]).seconds < self.cache_timeout:
                    return cached_data["data"]
                    
            # Fetch new news
            newsdata_articles = await self.fetch_newsdata_io(symbols)
            alpha_vantage_articles = await self.fetch_alpha_vantage_news(symbols)
            
            # Combine articles
            all_articles = newsdata_articles + alpha_vantage_articles
            
            # Remove duplicates based on title similarity
            unique_articles = []
            seen_titles = set()
            
            for article in all_articles:
                title_words = set(article["title"].lower().split())
                is_duplicate = any(
                    len(title_words.intersection(seen_title)) / len(title_words.union(seen_title)) > 0.7
                    for seen_title in seen_titles
                )
                
                if not is_duplicate:
                    unique_articles.append(article)
                    seen_titles.add(title_words)
                    
            # Analyze impact
            analysis = await self.analyze_news_impact(unique_articles, symbols)
            
            # Cache result
            result = {
                "articles": unique_articles[:20],  # Limit to 20 most recent
                "analysis": analysis
            }
            
            self.news_cache[cache_key] = {
                "data": result,
                "timestamp": current_time
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting cached news: {e}")
            return {"articles": [], "analysis": {}}
            
    async def close_connections(self):
        """Close all connections"""
        try:
            if self.session:
                await self.session.close()
                
            await self.sentiment_analyzer.close_connections()
            
        except Exception as e:
            logger.error(f"Error closing news service connections: {e}")
