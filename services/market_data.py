"""
Market Data Service for #IREKABITI_FX
Handles data from MetaTrader, Alpha Vantage, and Binance
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Optional import for MetaTrader5 (not available on all platforms)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

from binance.client import Client as BinanceClient
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

class MarketDataService:
    def __init__(self):
        self.mt5_initialized = False
        self.binance_client = None
        self.session = None
        self.initialize_connections()
        
    def initialize_connections(self):
        """Initialize connections to data sources"""
        # Initialize MetaTrader 5
        try:
            if mt5.initialize():
                if mt5.login(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER):
                    self.mt5_initialized = True
                    logger.info("✅ MetaTrader 5 connected successfully")
                else:
                    logger.error("❌ MetaTrader 5 login failed")
            else:
                logger.error("❌ MetaTrader 5 initialization failed")
        except Exception as e:
            logger.error(f"❌ MetaTrader 5 error: {e}")
            
        # Initialize Binance
        try:
            if settings.BINANCE_API_KEY and settings.BINANCE_SECRET_KEY:
                self.binance_client = BinanceClient(
                    api_key=settings.BINANCE_API_KEY,
                    api_secret=settings.BINANCE_SECRET_KEY
                )
                logger.info("✅ Binance connected successfully")
        except Exception as e:
            logger.error(f"❌ Binance connection error: {e}")
            
    async def get_forex_data(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """Get Forex data from MetaTrader 5"""
        if not self.mt5_initialized:
            logger.error("MetaTrader 5 not initialized")
            return None
            
        try:
            # Convert timeframe string to MT5 constant
            tf_map = {
                "5m": mt5.TIMEFRAME_M5,
                "15m": mt5.TIMEFRAME_M15,
                "1h": mt5.TIMEFRAME_H1,
                "4h": mt5.TIMEFRAME_H4,
                "1d": mt5.TIMEFRAME_D1
            }
            
            if timeframe not in tf_map:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
                
            rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, count)
            
            if rates is None or len(rates) == 0:
                logger.error(f"No data received for {symbol}")
                return None
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)
            
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            logger.error(f"Error getting Forex data for {symbol}: {e}")
            return None
            
    async def get_crypto_data(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """Get Crypto data from Binance"""
        if not self.binance_client:
            logger.error("Binance client not initialized")
            return None
            
        try:
            # Convert timeframe to Binance format
            tf_map = {
                "5m": "5m",
                "15m": "15m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d"
            }
            
            if timeframe not in tf_map:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
                
            klines = self.binance_client.get_klines(
                symbol=symbol,
                interval=tf_map[timeframe],
                limit=count
            )
            
            if not klines:
                logger.error(f"No data received for {symbol}")
                return None
                
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Convert to numeric
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col])
                
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            logger.error(f"Error getting Crypto data for {symbol}: {e}")
            return None
            
    async def get_alpha_vantage_data(self, symbol: str, function: str = "TIME_SERIES_DAILY") -> Optional[pd.DataFrame]:
        """Get data from Alpha Vantage API"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            logger.error("Alpha Vantage API key not configured")
            return None
            
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            url = "https://www.alphavantage.co/query"
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": settings.ALPHA_VANTAGE_API_KEY,
                "outputsize": "compact"
            }
            
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error: {data['Error Message']}")
                    return None
                    
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    return None
                    
                # Extract time series data
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key:
                        time_series_key = key
                        break
                        
                if not time_series_key:
                    logger.error("No time series data found")
                    return None
                    
                df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                # Rename columns
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                
                # Convert to numeric
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col])
                    
                return df
                
        except Exception as e:
            logger.error(f"Error getting Alpha Vantage data for {symbol}: {e}")
            return None
            
    async def get_market_data(self, symbol: str, timeframe: str, market_type: str = "forex") -> Optional[pd.DataFrame]:
        """Get market data based on market type"""
        if market_type.lower() == "forex":
            return await self.get_forex_data(symbol, timeframe)
        elif market_type.lower() == "crypto":
            return await self.get_crypto_data(symbol, timeframe)
        else:
            logger.error(f"Unknown market type: {market_type}")
            return None
            
    async def get_multiple_timeframes(self, symbol: str, market_type: str = "forex") -> Dict[str, pd.DataFrame]:
        """Get data for multiple timeframes"""
        results = {}
        
        for timeframe in settings.TIMEFRAMES:
            data = await self.get_market_data(symbol, timeframe, market_type)
            if data is not None:
                results[timeframe] = data
                
        return results
        
    async def get_current_price(self, symbol: str, market_type: str = "forex") -> Optional[float]:
        """Get current price for a symbol"""
        try:
            if market_type.lower() == "forex" and self.mt5_initialized:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    return (tick.bid + tick.ask) / 2
                    
            elif market_type.lower() == "crypto" and self.binance_client:
                ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
                if ticker:
                    return float(ticker['price'])
                    
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            
        return None
        
    async def get_market_status(self) -> Dict[str, bool]:
        """Get market status for different exchanges"""
        status = {
            "forex": False,
            "crypto": True  # Crypto markets are always open
        }
        
        try:
            # Check Forex market status (simplified)
            now = datetime.now()
            weekday = now.weekday()
            
            # Forex is closed on weekends (Saturday = 5, Sunday = 6)
            if weekday < 5:  # Monday to Friday
                status["forex"] = True
                
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            
        return status
        
    async def close_connections(self):
        """Close all connections"""
        try:
            if self.mt5_initialized:
                mt5.shutdown()
                
            if self.session:
                await self.session.close()
                
        except Exception as e:
            logger.error(f"Error closing connections: {e}")
            
    def __del__(self):
        """Cleanup on destruction"""
        try:
            if self.mt5_initialized:
                mt5.shutdown()
        except:
            pass
