"""
Sentiment Analysis Service for #IREKABITI_FX
Analyzes news and social media sentiment
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Optional imports for ML/NLP dependencies
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    tweepy = None
    TWEEPY_AVAILABLE = False

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    praw = None
    PRAW_AVAILABLE = False

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_analyzer = None
        self.twitter_api = None
        self.reddit_api = None
        self.session = None
        self.initialize_apis()
        self.initialize_models()
        
    def initialize_apis(self):
        """Initialize social media APIs"""
        try:
            # Twitter API v2
            if all([settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET, 
                   settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET]):
                auth = tweepy.OAuthHandler(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
                auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("✅ Twitter API initialized")
                
        except Exception as e:
            logger.error(f"Error initializing Twitter API: {e}")
            
        try:
            # Reddit API
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
            reddit_secret = os.getenv("REDDIT_SECRET", "")
            if reddit_client_id and reddit_secret:
                self.reddit_api = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_secret,
                    user_agent="IrekabiFX/1.0"
                )
                logger.info("✅ Reddit API initialized")
                
        except Exception as e:
            logger.error(f"Error initializing Reddit API: {e}")
            
    def initialize_models(self):
        """Initialize sentiment analysis models"""
        try:
            # Load pre-trained sentiment analysis model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            logger.info("✅ Sentiment analysis model loaded")
            
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            # Fallback to simpler model
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                logger.info("✅ Fallback sentiment model loaded")
            except Exception as e2:
                logger.error(f"Error loading fallback model: {e2}")
                
    async def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text"""
        try:
            if not self.sentiment_analyzer:
                return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
                
            results = self.sentiment_analyzer(text)
            
            # Convert to standard format
            sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            if isinstance(results[0], list):
                # Multiple scores format
                for result in results[0]:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if 'pos' in label:
                        sentiment_scores['positive'] = score
                    elif 'neg' in label:
                        sentiment_scores['negative'] = score
                    else:
                        sentiment_scores['neutral'] = score
            else:
                # Single score format
                label = results[0]['label'].lower()
                score = results[0]['score']
                
                if 'pos' in label:
                    sentiment_scores['positive'] = score
                    sentiment_scores['negative'] = 1 - score
                else:
                    sentiment_scores['negative'] = score
                    sentiment_scores['positive'] = 1 - score
                    
            return sentiment_scores
            
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            
    async def get_twitter_sentiment(self, symbol: str, count: int = 100) -> Dict[str, float]:
        """Get Twitter sentiment for a trading symbol"""
        try:
            if not self.twitter_api:
                return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
                
            # Create search queries for the symbol
            queries = [f"${symbol}", f"{symbol}USD", f"{symbol} trading", f"{symbol} forex"]
            
            all_tweets = []
            for query in queries:
                try:
                    tweets = tweepy.Cursor(
                        self.twitter_api.search_tweets,
                        q=query,
                        lang='en',
                        result_type='recent',
                        tweet_mode='extended'
                    ).items(count // len(queries))
                    
                    for tweet in tweets:
                        all_tweets.append(tweet.full_text)
                        
                except Exception as e:
                    logger.error(f"Error fetching tweets for {query}: {e}")
                    
            if not all_tweets:
                return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
                
            # Analyze sentiment for all tweets
            sentiment_totals = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            for tweet in all_tweets:
                sentiment = await self.analyze_text_sentiment(tweet)
                for key in sentiment_totals:
                    sentiment_totals[key] += sentiment[key]
                    
            # Calculate averages
            tweet_count = len(all_tweets)
            sentiment_averages = {
                key: value / tweet_count for key, value in sentiment_totals.items()
            }
            sentiment_averages['volume'] = tweet_count
            
            return sentiment_averages
            
        except Exception as e:
            logger.error(f"Error getting Twitter sentiment for {symbol}: {e}")
            return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
            
    async def get_reddit_sentiment(self, symbol: str, count: int = 50) -> Dict[str, float]:
        """Get Reddit sentiment for a trading symbol"""
        try:
            if not self.reddit_api:
                return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
                
            # Search relevant subreddits
            subreddits = ['forex', 'trading', 'cryptocurrency', 'investing', 'wallstreetbets']
            all_posts = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit_api.subreddit(subreddit_name)
                    
                    # Search for symbol mentions
                    for submission in subreddit.search(symbol, limit=count // len(subreddits)):
                        all_posts.append(submission.title + " " + submission.selftext)
                        
                        # Include top comments
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments[:3]:
                            if hasattr(comment, 'body'):
                                all_posts.append(comment.body)
                                
                except Exception as e:
                    logger.error(f"Error fetching Reddit posts from {subreddit_name}: {e}")
                    
            if not all_posts:
                return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
                
            # Analyze sentiment
            sentiment_totals = {'positive': 0, 'neutral': 0, 'negative': 0}
            
            for post in all_posts:
                if len(post.strip()) > 10:  # Filter out very short posts
                    sentiment = await self.analyze_text_sentiment(post)
                    for key in sentiment_totals:
                        sentiment_totals[key] += sentiment[key]
                        
            # Calculate averages
            post_count = len(all_posts)
            sentiment_averages = {
                key: value / post_count for key, value in sentiment_totals.items()
            }
            sentiment_averages['volume'] = post_count
            
            return sentiment_averages
            
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment for {symbol}: {e}")
            return {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 'volume': 0}
            
    async def get_combined_sentiment(self, symbol: str) -> Dict[str, any]:
        """Get combined sentiment from all sources"""
        try:
            # Get sentiment from all sources
            twitter_sentiment = await self.get_twitter_sentiment(symbol)
            reddit_sentiment = await self.get_reddit_sentiment(symbol)
            
            # Weight by volume
            twitter_weight = min(twitter_sentiment['volume'] / 100, 1.0)
            reddit_weight = min(reddit_sentiment['volume'] / 50, 1.0)
            
            total_weight = twitter_weight + reddit_weight
            
            if total_weight == 0:
                return {
                    'positive': 0.33,
                    'neutral': 0.34,
                    'negative': 0.33,
                    'sentiment_score': 0,
                    'total_volume': 0,
                    'sources': {
                        'twitter': twitter_sentiment,
                        'reddit': reddit_sentiment
                    }
                }
                
            # Calculate weighted average
            combined_sentiment = {}
            for key in ['positive', 'neutral', 'negative']:
                combined_sentiment[key] = (
                    (twitter_sentiment[key] * twitter_weight + 
                     reddit_sentiment[key] * reddit_weight) / total_weight
                )
                
            # Calculate sentiment score (-1 to 1)
            sentiment_score = combined_sentiment['positive'] - combined_sentiment['negative']
            
            return {
                'positive': combined_sentiment['positive'],
                'neutral': combined_sentiment['neutral'],
                'negative': combined_sentiment['negative'],
                'sentiment_score': sentiment_score,
                'total_volume': twitter_sentiment['volume'] + reddit_sentiment['volume'],
                'sources': {
                    'twitter': twitter_sentiment,
                    'reddit': reddit_sentiment
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting combined sentiment for {symbol}: {e}")
            return {
                'positive': 0.33,
                'neutral': 0.34,
                'negative': 0.33,
                'sentiment_score': 0,
                'total_volume': 0,
                'sources': {}
            }
            
    async def get_market_sentiment_summary(self, symbols: List[str]) -> Dict[str, any]:
        """Get sentiment summary for multiple symbols"""
        try:
            tasks = [self.get_combined_sentiment(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            sentiment_data = {}
            total_positive = 0
            total_negative = 0
            total_volume = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error getting sentiment for {symbols[i]}: {result}")
                    continue
                    
                symbol = symbols[i]
                sentiment_data[symbol] = result
                
                total_positive += result['positive']
                total_negative += result['negative']
                total_volume += result['total_volume']
                
            # Calculate overall market sentiment
            symbol_count = len(sentiment_data)
            if symbol_count > 0:
                avg_positive = total_positive / symbol_count
                avg_negative = total_negative / symbol_count
                market_sentiment_score = avg_positive - avg_negative
            else:
                market_sentiment_score = 0
                
            return {
                'symbols': sentiment_data,
                'market_sentiment_score': market_sentiment_score,
                'total_volume': total_volume,
                'symbol_count': symbol_count,
                'summary': self._generate_sentiment_summary(market_sentiment_score)
            }
            
        except Exception as e:
            logger.error(f"Error getting market sentiment summary: {e}")
            return {
                'symbols': {},
                'market_sentiment_score': 0,
                'total_volume': 0,
                'symbol_count': 0,
                'summary': 'Neutral market sentiment'
            }
            
    def _generate_sentiment_summary(self, sentiment_score: float) -> str:
        """Generate human-readable sentiment summary"""
        if sentiment_score > 0.3:
            return "🟢 Bullish market sentiment - Positive social media activity"
        elif sentiment_score > 0.1:
            return "🟡 Slightly bullish sentiment - Mild positive activity"
        elif sentiment_score > -0.1:
            return "⚪ Neutral market sentiment - Balanced social media activity"
        elif sentiment_score > -0.3:
            return "🟡 Slightly bearish sentiment - Mild negative activity"
        else:
            return "🔴 Bearish market sentiment - Negative social media activity"
            
    async def close_connections(self):
        """Close all connections"""
        try:
            if self.session:
                await self.session.close()
        except Exception as e:
            logger.error(f"Error closing sentiment analysis connections: {e}")
