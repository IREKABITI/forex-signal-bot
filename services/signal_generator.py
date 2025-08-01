"""
Signal Generator Service for #IREKABITI_FX
Core ML-powered signal generation with multi-timeframe analysis
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from services.market_data import MarketDataService
from services.technical_analysis import TechnicalAnalysis
from services.ml_analysis import MLAnalysis
from services.sentiment_analysis import SentimentAnalysis
from services.news_service import NewsService
from database.db_manager import DatabaseManager
from models.trading_models import TradingSignal, SignalConfidence
from config.settings import settings
from utils.logger import setup_logger
from utils.validators import validate_symbol, validate_timeframe

logger = setup_logger()

class SignalGenerator:
    def __init__(self):
        self.market_data = MarketDataService()
        self.technical_analysis = TechnicalAnalysis()
        self.ml_analysis = MLAnalysis()
        self.sentiment_analysis = SentimentAnalysis()
        self.news_service = NewsService()
        self.db_manager = DatabaseManager()
        self.signal_cache = {}
        self.cache_duration = 300  # 5 minutes
        
    async def generate_signal(self, symbol: str, timeframe: str = "1h") -> Optional[TradingSignal]:
        """Generate a comprehensive trading signal for a symbol"""
        try:
            logger.info(f"Generating signal for {symbol} on {timeframe}")
            
            # Validate inputs
            if not validate_symbol(symbol) or not validate_timeframe(timeframe):
                logger.error(f"Invalid symbol or timeframe: {symbol}, {timeframe}")
                return None
                
            # Check if we're in a valid trading session
            if not self._is_trading_session_active(symbol):
                logger.info(f"Trading session not active for {symbol}")
                return None
                
            # Get market data for multiple timeframes
            market_type = "crypto" if symbol.endswith("USDT") else "forex"
            
            # Primary timeframe analysis
            primary_data = await self.market_data.get_market_data(symbol, timeframe, market_type)
            if primary_data is None or len(primary_data) < 100:
                logger.error(f"Insufficient data for {symbol}")
                return None
                
            # Multi-timeframe analysis
            timeframes_data = await self.market_data.get_multiple_timeframes(symbol, market_type)
            
            # Technical analysis
            technical_signals = {}
            for tf, data in timeframes_data.items():
                if data is not None and len(data) >= 50:
                    indicators = self.technical_analysis.calculate_all_indicators(data)
                    signal = self.technical_analysis.generate_signals(data)
                    technical_signals[tf] = {
                        'signal': signal,
                        'indicators': indicators
                    }
                    
            if not technical_signals:
                logger.error(f"No technical signals generated for {symbol}")
                return None
                
            # ML Analysis
            primary_indicators = technical_signals.get(timeframe, {}).get('indicators', {})
            ml_prediction = await asyncio.create_task(
                asyncio.to_thread(self.ml_analysis.predict_signal, symbol, primary_data, primary_indicators)
            )
            
            # Sentiment Analysis
            sentiment_data = await self.sentiment_analysis.get_combined_sentiment(symbol)
            
            # News Analysis
            news_data = await self.news_service.get_cached_news([symbol])
            
            # Combine all analyses
            signal = await self._combine_analyses(
                symbol, timeframe, technical_signals, ml_prediction, 
                sentiment_data, news_data, primary_data
            )
            
            if signal and signal.confidence >= settings.MIN_SIGNAL_SCORE:
                # Store signal in database
                await self.db_manager.store_signal(signal)
                
                # Cache signal
                cache_key = f"{symbol}_{timeframe}"
                self.signal_cache[cache_key] = {
                    'signal': signal,
                    'timestamp': datetime.now()
                }
                
                logger.info(f"✅ Generated signal for {symbol}: {signal.direction} with {signal.confidence}% confidence")
                return signal
            else:
                logger.info(f"Signal for {symbol} below minimum confidence threshold")
                return None
                
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
            
    async def _combine_analyses(self, symbol: str, timeframe: str, technical_signals: Dict, 
                               ml_prediction: Dict, sentiment_data: Dict, news_data: Dict, 
                               price_data: pd.DataFrame) -> Optional[TradingSignal]:
        """Combine all analysis types into a final signal"""
        try:
            current_price = price_data['Close'].iloc[-1]
            
            # Initialize scoring
            bullish_score = 0
            bearish_score = 0
            confidence_factors = []
            analysis_reasons = []
            
            # Technical Analysis Scoring (40% weight)
            primary_technical = technical_signals.get(timeframe, {}).get('signal', {})
            
            if primary_technical.get('direction') == 'BUY':
                bullish_score += primary_technical.get('strength', 0) * 0.4
                analysis_reasons.extend(primary_technical.get('reasons', []))
            elif primary_technical.get('direction') == 'SELL':
                bearish_score += primary_technical.get('strength', 0) * 0.4
                analysis_reasons.extend(primary_technical.get('reasons', []))
                
            confidence_factors.append(primary_technical.get('confidence', 50))
            
            # Multi-timeframe confirmation (20% weight)
            mtf_bullish = 0
            mtf_bearish = 0
            
            for tf, data in technical_signals.items():
                if tf != timeframe:  # Exclude primary timeframe
                    signal = data.get('signal', {})
                    if signal.get('direction') == 'BUY':
                        mtf_bullish += 1
                    elif signal.get('direction') == 'SELL':
                        mtf_bearish += 1
                        
            if mtf_bullish > mtf_bearish:
                bullish_score += 20
                analysis_reasons.append(f"Multi-timeframe bullish confirmation ({mtf_bullish}/{len(technical_signals)-1})")
            elif mtf_bearish > mtf_bullish:
                bearish_score += 20
                analysis_reasons.append(f"Multi-timeframe bearish confirmation ({mtf_bearish}/{len(technical_signals)-1})")
                
            # ML Analysis Scoring (25% weight)
            ml_prediction_value = ml_prediction.get('prediction', 0)
            ml_confidence = ml_prediction.get('confidence', 0)
            
            if ml_prediction_value == 1:  # Buy signal
                bullish_score += 25
                analysis_reasons.append(f"ML model predicts BUY ({ml_confidence:.1f}% confidence)")
            elif ml_prediction_value == -1:  # Sell signal
                bearish_score += 25
                analysis_reasons.append(f"ML model predicts SELL ({ml_confidence:.1f}% confidence)")
                
            confidence_factors.append(ml_confidence)
            
            # Sentiment Analysis Scoring (10% weight)
            sentiment_score = sentiment_data.get('sentiment_score', 0)
            
            if sentiment_score > 0.2:
                bullish_score += 10
                analysis_reasons.append("Positive market sentiment")
            elif sentiment_score < -0.2:
                bearish_score += 10
                analysis_reasons.append("Negative market sentiment")
                
            # News Analysis Scoring (5% weight)
            news_analysis = news_data.get('analysis', {})
            news_sentiment = news_analysis.get('overall_sentiment', 0)
            
            if news_sentiment > 0.2:
                bullish_score += 5
                analysis_reasons.append("Positive news sentiment")
            elif news_sentiment < -0.2:
                bearish_score += 5
                analysis_reasons.append("Negative news sentiment")
                
            # Determine final direction and confidence
            total_score = bullish_score + bearish_score
            
            if total_score < 30:  # Minimum signal strength
                return None
                
            if bullish_score > bearish_score:
                direction = "BUY"
                strength = bullish_score
            else:
                direction = "SELL"
                strength = bearish_score
                
            # Calculate confidence (weighted average of factors)
            base_confidence = (strength / 100) * 100  # Convert to percentage
            avg_factor_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 50
            
            final_confidence = int((base_confidence * 0.7) + (avg_factor_confidence * 0.3))
            final_confidence = max(30, min(95, final_confidence))  # Clamp between 30-95
            
            # Calculate entry, TP, and SL
            entry_price = current_price
            atr = self._calculate_atr(price_data)
            
            if direction == "BUY":
                tp_price = entry_price + (atr * 2.5)
                sl_price = entry_price - (atr * 1.5)
            else:
                tp_price = entry_price - (atr * 2.5)
                sl_price = entry_price + (atr * 1.5)
                
            # Calculate risk percentage
            risk_distance = abs(entry_price - sl_price)
            risk_percent = (risk_distance / entry_price) * 100
            
            # Create signal object
            signal = TradingSignal(
                symbol=symbol,
                direction=direction,
                entry_price=round(entry_price, 5),
                tp_price=round(tp_price, 5),
                sl_price=round(sl_price, 5),
                confidence=final_confidence,
                timeframe=timeframe,
                risk_percent=round(risk_percent, 2),
                analysis="; ".join(analysis_reasons[:3]),  # Top 3 reasons
                timestamp=datetime.now(),
                market_type="crypto" if symbol.endswith("USDT") else "forex",
                strength=int(strength),
                sentiment_score=sentiment_score,
                news_impact=news_sentiment
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error combining analyses for {symbol}: {e}")
            return None
            
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(period).mean().iloc[-1]
            
            return atr if not pd.isna(atr) else data['Close'].iloc[-1] * 0.01
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.01
            
    def _is_trading_session_active(self, symbol: str) -> bool:
        """Check if trading session is active for the symbol"""
        try:
            if symbol.endswith("USDT"):  # Crypto markets are always open
                return True
                
            # Check Forex trading sessions (London & New York only)
            now = datetime.utcnow()
            current_hour = now.hour
            current_weekday = now.weekday()
            
            # No trading on weekends
            if current_weekday >= 5:  # Saturday = 5, Sunday = 6
                return False
                
            # London session: 8:00-17:00 UTC
            # New York session: 13:00-22:00 UTC
            london_active = 8 <= current_hour < 17
            new_york_active = 13 <= current_hour < 22
            
            return london_active or new_york_active
            
        except Exception as e:
            logger.error(f"Error checking trading session: {e}")
            return False
            
    async def get_latest_signals(self, limit: int = 10) -> List[Dict]:
        """Get latest generated signals"""
        try:
            signals = await self.db_manager.get_recent_signals(limit)
            
            result = []
            for signal in signals:
                result.append({
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'entry_price': signal.entry_price,
                    'tp_price': signal.tp_price,
                    'sl_price': signal.sl_price,
                    'confidence': signal.confidence,
                    'risk_percent': signal.risk_percent,
                    'analysis': signal.analysis,
                    'timestamp': signal.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'timeframe': signal.timeframe,
                    'market_type': signal.market_type
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting latest signals: {e}")
            return []
            
    async def scan_all_markets(self) -> Dict[str, any]:
        """Scan all configured markets for opportunities"""
        try:
            logger.info("Starting comprehensive market scan")
            
            all_pairs = settings.TRADING_PAIRS_FOREX + settings.TRADING_PAIRS_CRYPTO
            scan_results = {
                'forex_count': 0,
                'crypto_count': 0,
                'high_confidence': 0,
                'total_scanned': 0,
                'top_signals': [],
                'scan_timestamp': datetime.now().isoformat()
            }
            
            # Create tasks for parallel processing
            tasks = []
            for symbol in all_pairs:
                for timeframe in ['1h', '4h']:  # Focus on higher timeframes for scanning
                    task = asyncio.create_task(self.generate_signal(symbol, timeframe))
                    tasks.append((symbol, timeframe, task))
                    
            # Process results
            all_signals = []
            
            for symbol, timeframe, task in tasks:
                try:
                    signal = await task
                    scan_results['total_scanned'] += 1
                    
                    if signal:
                        if signal.market_type == "forex":
                            scan_results['forex_count'] += 1
                        else:
                            scan_results['crypto_count'] += 1
                            
                        if signal.confidence >= 80:
                            scan_results['high_confidence'] += 1
                            
                        all_signals.append({
                            'symbol': signal.symbol,
                            'direction': signal.direction,
                            'confidence': signal.confidence,
                            'timeframe': signal.timeframe,
                            'entry_price': signal.entry_price,
                            'risk_percent': signal.risk_percent
                        })
                        
                except Exception as e:
                    logger.error(f"Error scanning {symbol} {timeframe}: {e}")
                    
            # Sort by confidence and get top signals
            all_signals.sort(key=lambda x: x['confidence'], reverse=True)
            scan_results['top_signals'] = all_signals[:10]
            
            logger.info(f"Market scan completed: {scan_results['forex_count']} forex, {scan_results['crypto_count']} crypto opportunities")
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Error in market scan: {e}")
            return {
                'forex_count': 0,
                'crypto_count': 0,
                'high_confidence': 0,
                'total_scanned': 0,
                'top_signals': [],
                'error': str(e)
            }
            
    async def backtest_signal_accuracy(self, days: int = 30) -> Dict[str, any]:
        """Backtest signal accuracy over specified period"""
        try:
            # Get historical signals
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            historical_signals = await self.db_manager.get_signals_in_range(start_date, end_date)
            
            if not historical_signals:
                return {
                    'total_signals': 0,
                    'accuracy': 0,
                    'avg_return': 0,
                    'best_signal': 0,
                    'worst_signal': 0
                }
                
            successful_signals = 0
            total_return = 0
            signal_returns = []
            
            for signal in historical_signals:
                # Simulate signal outcome based on TP/SL hit
                # This is a simplified backtest - in production, you'd use actual price data
                
                # Get price data after signal
                market_type = signal.market_type
                future_data = await self.market_data.get_market_data(
                    signal.symbol, "1h", market_type
                )
                
                if future_data is not None and len(future_data) > 0:
                    # Find if TP or SL was hit first
                    entry_price = signal.entry_price
                    tp_price = signal.tp_price
                    sl_price = signal.sl_price
                    
                    signal_return = self._calculate_signal_return(
                        future_data, entry_price, tp_price, sl_price, signal.direction
                    )
                    
                    if signal_return > 0:
                        successful_signals += 1
                        
                    total_return += signal_return
                    signal_returns.append(signal_return)
                    
            accuracy = (successful_signals / len(historical_signals)) * 100 if historical_signals else 0
            avg_return = total_return / len(historical_signals) if historical_signals else 0
            best_signal = max(signal_returns) if signal_returns else 0
            worst_signal = min(signal_returns) if signal_returns else 0
            
            return {
                'total_signals': len(historical_signals),
                'successful_signals': successful_signals,
                'accuracy': round(accuracy, 2),
                'avg_return': round(avg_return, 2),
                'best_signal': round(best_signal, 2),
                'worst_signal': round(worst_signal, 2),
                'backtest_period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return {'error': str(e)}
            
    def _calculate_signal_return(self, price_data: pd.DataFrame, entry: float, 
                               tp: float, sl: float, direction: str) -> float:
        """Calculate signal return based on TP/SL hit"""
        try:
            if direction == "BUY":
                tp_return = (tp - entry) / entry
                sl_return = (sl - entry) / entry
            else:
                tp_return = (entry - tp) / entry
                sl_return = (entry - sl) / entry
                
            # Simplified logic - check if any price hit TP or SL
            max_favorable = price_data['High'].max() if direction == "BUY" else price_data['Low'].min()
            max_adverse = price_data['Low'].min() if direction == "BUY" else price_data['High'].max()
            
            if direction == "BUY":
                if max_favorable >= tp:
                    return tp_return
                elif max_adverse <= sl:
                    return sl_return
            else:
                if max_favorable <= tp:
                    return tp_return
                elif max_adverse >= sl:
                    return sl_return
                    
            # If neither TP nor SL hit, return current profit/loss
            current_price = price_data['Close'].iloc[-1]
            if direction == "BUY":
                return (current_price - entry) / entry
            else:
                return (entry - current_price) / entry
                
        except Exception as e:
            logger.error(f"Error calculating signal return: {e}")
            return 0
            
    async def get_signal_performance_stats(self) -> Dict[str, any]:
        """Get comprehensive signal performance statistics"""
        try:
            # Get all signals from last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            signals = await self.db_manager.get_signals_in_range(start_date, end_date)
            
            if not signals:
                return {
                    'total_signals': 0,
                    'avg_confidence': 0,
                    'symbol_breakdown': {},
                    'timeframe_breakdown': {},
                    'direction_breakdown': {}
                }
                
            # Calculate statistics
            total_signals = len(signals)
            avg_confidence = sum(s.confidence for s in signals) / total_signals
            
            symbol_breakdown = {}
            timeframe_breakdown = {}
            direction_breakdown = {'BUY': 0, 'SELL': 0}
            
            for signal in signals:
                # Symbol breakdown
                if signal.symbol not in symbol_breakdown:
                    symbol_breakdown[signal.symbol] = 0
                symbol_breakdown[signal.symbol] += 1
                
                # Timeframe breakdown
                if signal.timeframe not in timeframe_breakdown:
                    timeframe_breakdown[signal.timeframe] = 0
                timeframe_breakdown[signal.timeframe] += 1
                
                # Direction breakdown
                direction_breakdown[signal.direction] += 1
                
            return {
                'total_signals': total_signals,
                'avg_confidence': round(avg_confidence, 1),
                'symbol_breakdown': symbol_breakdown,
                'timeframe_breakdown': timeframe_breakdown,
                'direction_breakdown': direction_breakdown,
                'period_days': 30
            }
            
        except Exception as e:
            logger.error(f"Error getting signal performance stats: {e}")
            return {'error': str(e)}
