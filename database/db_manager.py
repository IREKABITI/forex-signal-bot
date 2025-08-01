"""
Database Manager for #IREKABITI_FX
Handles SQLite database operations and data persistence
"""

import sqlite3
import aiosqlite
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import asyncio
from dataclasses import asdict

from models.trading_models import TradingSignal, SignalConfidence
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

class DatabaseManager:
    def __init__(self):
        self.db_path = "irekabiti_fx.db"
        self.initialized = False
        
    async def initialize(self):
        """Initialize database tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Trading signals table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS trading_signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        tp_price REAL NOT NULL,
                        sl_price REAL NOT NULL,
                        confidence INTEGER NOT NULL,
                        timeframe TEXT NOT NULL,
                        risk_percent REAL NOT NULL,
                        analysis TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        market_type TEXT NOT NULL,
                        strength INTEGER DEFAULT 0,
                        sentiment_score REAL DEFAULT 0,
                        news_impact REAL DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        result TEXT DEFAULT NULL,
                        pnl REAL DEFAULT NULL,
                        closed_at DATETIME DEFAULT NULL
                    )
                """)
                
                # User subscriptions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        settings TEXT DEFAULT '{}',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        UNIQUE(user_id, platform)
                    )
                """)
                
                # Portfolio data table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        total_value REAL NOT NULL,
                        daily_pnl REAL NOT NULL,
                        signals_count INTEGER DEFAULT 0,
                        win_rate REAL DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # News data table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS news_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        source TEXT,
                        sentiment_score REAL DEFAULT 0,
                        impact_score REAL DEFAULT 0,
                        symbols TEXT,
                        published_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Market data cache table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS market_data_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        data TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, timeframe)
                    )
                """)
                
                # Signal performance tracking
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS signal_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        signal_id INTEGER NOT NULL,
                        check_time DATETIME NOT NULL,
                        current_price REAL NOT NULL,
                        unrealized_pnl REAL NOT NULL,
                        status TEXT NOT NULL,
                        FOREIGN KEY (signal_id) REFERENCES trading_signals (id)
                    )
                """)
                
                # Create indexes for better performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON trading_signals(timestamp)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_signals_confidence ON trading_signals(confidence)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_date ON portfolio_data(date)")
                
                await db.commit()
                
            self.initialized = True
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
            
    async def store_signal(self, signal: TradingSignal) -> bool:
        """Store a trading signal in the database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO trading_signals 
                    (symbol, direction, entry_price, tp_price, sl_price, confidence, 
                     timeframe, risk_percent, analysis, timestamp, market_type, 
                     strength, sentiment_score, news_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal.symbol, signal.direction, signal.entry_price, signal.tp_price,
                    signal.sl_price, signal.confidence, signal.timeframe, signal.risk_percent,
                    signal.analysis, signal.timestamp, signal.market_type, signal.strength,
                    signal.sentiment_score, signal.news_impact
                ))
                await db.commit()
                
            logger.info(f"✅ Signal stored: {signal.symbol} {signal.direction}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing signal: {e}")
            return False
            
    async def get_recent_signals(self, limit: int = 10) -> List[TradingSignal]:
        """Get recent trading signals"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT * FROM trading_signals 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                signals = []
                for row in rows:
                    signal = TradingSignal(
                        symbol=row['symbol'],
                        direction=row['direction'],
                        entry_price=row['entry_price'],
                        tp_price=row['tp_price'],
                        sl_price=row['sl_price'],
                        confidence=row['confidence'],
                        timeframe=row['timeframe'],
                        risk_percent=row['risk_percent'],
                        analysis=row['analysis'],
                        timestamp=datetime.fromisoformat(row['timestamp']) if isinstance(row['timestamp'], str) else row['timestamp'],
                        market_type=row['market_type'],
                        strength=row['strength'],
                        sentiment_score=row['sentiment_score'],
                        news_impact=row['news_impact']
                    )
                    signals.append(signal)
                    
                return signals
                
        except Exception as e:
            logger.error(f"❌ Error getting recent signals: {e}")
            return []
            
    async def get_signals_in_range(self, start_date: datetime, end_date: datetime) -> List[TradingSignal]:
        """Get signals within a date range"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute("""
                    SELECT * FROM trading_signals 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                rows = await cursor.fetchall()
                
                signals = []
                for row in rows:
                    signal = TradingSignal(
                        symbol=row['symbol'],
                        direction=row['direction'],
                        entry_price=row['entry_price'],
                        tp_price=row['tp_price'],
                        sl_price=row['sl_price'],
                        confidence=row['confidence'],
                        timeframe=row['timeframe'],
                        risk_percent=row['risk_percent'],
                        analysis=row['analysis'],
                        timestamp=datetime.fromisoformat(row['timestamp']) if isinstance(row['timestamp'], str) else row['timestamp'],
                        market_type=row['market_type'],
                        strength=row['strength'],
                        sentiment_score=row['sentiment_score'],
                        news_impact=row['news_impact']
                    )
                    signals.append(signal)
                    
                return signals
                
        except Exception as e:
            logger.error(f"❌ Error getting signals in range: {e}")
            return []
            
    async def update_signal_result(self, signal_id: int, result: str, pnl: float):
        """Update signal with final result"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE trading_signals 
                    SET result = ?, pnl = ?, closed_at = ?, status = 'closed'
                    WHERE id = ?
                """, (result, pnl, datetime.now(), signal_id))
                await db.commit()
                
            logger.info(f"✅ Signal {signal_id} updated with result: {result}")
            
        except Exception as e:
            logger.error(f"❌ Error updating signal result: {e}")
            
    async def store_user_subscription(self, user_id: str, platform: str, settings: Dict = None):
        """Store user subscription"""
        try:
            settings_json = json.dumps(settings or {})
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_subscriptions 
                    (user_id, platform, settings)
                    VALUES (?, ?, ?)
                """, (user_id, platform, settings_json))
                await db.commit()
                
            logger.info(f"✅ User subscription stored: {user_id} on {platform}")
            
        except Exception as e:
            logger.error(f"❌ Error storing user subscription: {e}")
            
    async def get_subscribed_users(self, platform: str) -> List[str]:
        """Get subscribed users for a platform"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id FROM user_subscriptions 
                    WHERE platform = ? AND is_active = 1
                """, (platform,))
                
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Error getting subscribed users: {e}")
            return []
            
    async def get_subscribed_channels(self, platform: str) -> List[int]:
        """Get subscribed channels for Discord"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id FROM user_subscriptions 
                    WHERE platform = ? AND is_active = 1
                """, (platform,))
                
                rows = await cursor.fetchall()
                return [int(row[0]) for row in rows if row[0].isdigit()]
                
        except Exception as e:
            logger.error(f"❌ Error getting subscribed channels: {e}")
            return []
            
    async def store_portfolio_data(self, date: datetime, total_value: float, daily_pnl: float, 
                                 signals_count: int, win_rate: float):
        """Store daily portfolio data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO portfolio_data 
                    (date, total_value, daily_pnl, signals_count, win_rate)
                    VALUES (?, ?, ?, ?, ?)
                """, (date.date(), total_value, daily_pnl, signals_count, win_rate))
                await db.commit()
                
        except Exception as e:
            logger.error(f"❌ Error storing portfolio data: {e}")
            
    async def get_daily_report(self) -> Dict[str, Any]:
        """Get daily performance report"""
        try:
            today = datetime.now().date()
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get today's signals
                cursor = await db.execute("""
                    SELECT COUNT(*) as total, 
                           AVG(confidence) as avg_confidence,
                           SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins
                    FROM trading_signals 
                    WHERE DATE(timestamp) = ?
                """, (today,))
                
                signal_stats = await cursor.fetchone()
                
                # Get portfolio data
                cursor = await db.execute("""
                    SELECT * FROM portfolio_data 
                    WHERE date = ?
                """, (today,))
                
                portfolio_row = await cursor.fetchone()
                
                total_signals = signal_stats[0] or 0
                successful_signals = signal_stats[2] or 0
                win_rate = (successful_signals / total_signals * 100) if total_signals > 0 else 0
                avg_confidence = signal_stats[1] or 0
                
                # Get best performing signal
                cursor = await db.execute("""
                    SELECT symbol, pnl FROM trading_signals 
                    WHERE DATE(timestamp) = ? AND pnl IS NOT NULL
                    ORDER BY pnl DESC LIMIT 1
                """, (today,))
                
                best_signal_row = await cursor.fetchone()
                best_signal = f"{best_signal_row[0]} (+{best_signal_row[1]:.2f}%)" if best_signal_row else "N/A"
                
                return {
                    'total_signals': total_signals,
                    'successful_signals': successful_signals,
                    'win_rate': win_rate,
                    'avg_confidence': avg_confidence,
                    'total_pnl': portfolio_row[2] if portfolio_row else 0,
                    'best_signal': best_signal,
                    'active_pairs': len(set([row[0] for row in await db.execute("SELECT DISTINCT symbol FROM trading_signals WHERE DATE(timestamp) = ?", (today,)).fetchall()]))
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting daily report: {e}")
            return {
                'total_signals': 0,
                'successful_signals': 0,
                'win_rate': 0,
                'avg_confidence': 0,
                'total_pnl': 0,
                'best_signal': 'N/A',
                'active_pairs': 0
            }
            
    async def get_trading_stats(self) -> Dict[str, Any]:
        """Get comprehensive trading statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Overall stats
                cursor = await db.execute("""
                    SELECT COUNT(*) as total,
                           AVG(confidence) as avg_confidence,
                           SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                           AVG(pnl) as avg_pnl,
                           MAX(pnl) as best_signal,
                           MIN(pnl) as worst_signal
                    FROM trading_signals 
                    WHERE result IS NOT NULL
                """)
                
                stats = await cursor.fetchone()
                
                # Calculate win rate
                total_signals = stats[0] or 0
                wins = stats[2] or 0
                win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
                
                # Get active days
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM trading_signals
                """)
                
                active_days = (await cursor.fetchone())[0] or 0
                
                # Get top performing pairs
                cursor = await db.execute("""
                    SELECT symbol, AVG(pnl) as avg_pnl
                    FROM trading_signals 
                    WHERE result IS NOT NULL
                    GROUP BY symbol
                    ORDER BY avg_pnl DESC
                    LIMIT 5
                """)
                
                top_pairs = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # Calculate Sharpe ratio (simplified)
                cursor = await db.execute("""
                    SELECT pnl FROM trading_signals 
                    WHERE result IS NOT NULL AND pnl IS NOT NULL
                """)
                
                pnl_values = [row[0] for row in await cursor.fetchall()]
                
                if pnl_values:
                    returns = pd.Series(pnl_values)
                    sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
                    max_drawdown = returns.cumsum().expanding().max().subtract(returns.cumsum()).max()
                else:
                    sharpe_ratio = 0
                    max_drawdown = 0
                
                return {
                    'total_signals': total_signals,
                    'win_rate': win_rate,
                    'total_return': stats[3] or 0,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'best_signal': stats[4] or 0,
                    'active_days': active_days,
                    'avg_confidence': stats[1] or 0,
                    'top_pairs': top_pairs
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting trading stats: {e}")
            return {
                'total_signals': 0,
                'win_rate': 0,
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'best_signal': 0,
                'active_days': 0,
                'avg_confidence': 0,
                'top_pairs': {}
            }
            
    async def store_news_data(self, title: str, content: str, source: str, 
                            sentiment_score: float, symbols: List[str]):
        """Store news data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO news_data 
                    (title, content, source, sentiment_score, symbols)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, content, source, sentiment_score, ','.join(symbols)))
                await db.commit()
                
        except Exception as e:
            logger.error(f"❌ Error storing news data: {e}")
            
    async def cache_market_data(self, symbol: str, timeframe: str, data: str):
        """Cache market data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO market_data_cache 
                    (symbol, timeframe, data, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (symbol, timeframe, data, datetime.now()))
                await db.commit()
                
        except Exception as e:
            logger.error(f"❌ Error caching market data: {e}")
            
    async def get_cached_market_data(self, symbol: str, timeframe: str, max_age_minutes: int = 5) -> Optional[str]:
        """Get cached market data if still valid"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT data FROM market_data_cache 
                    WHERE symbol = ? AND timeframe = ? AND timestamp > ?
                """, (symbol, timeframe, cutoff_time))
                
                row = await cursor.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"❌ Error getting cached market data: {e}")
            return None
            
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to prevent database bloat"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Clean old signals
                await db.execute("""
                    DELETE FROM trading_signals 
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Clean old news data
                await db.execute("""
                    DELETE FROM news_data 
                    WHERE created_at < ?
                """, (cutoff_date,))
                
                # Clean old market data cache
                cache_cutoff = datetime.now() - timedelta(days=1)
                await db.execute("""
                    DELETE FROM market_data_cache 
                    WHERE timestamp < ?
                """, (cache_cutoff,))
                
                await db.commit()
                
            logger.info(f"✅ Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {e}")
            
    async def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Count records in each table
                tables = ['trading_signals', 'user_subscriptions', 'portfolio_data', 
                         'news_data', 'market_data_cache', 'signal_performance']
                
                for table in tables:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = (await cursor.fetchone())[0]
                    stats[table] = count
                    
                return stats
                
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {}
