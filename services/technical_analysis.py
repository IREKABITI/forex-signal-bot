"""
Technical Analysis Service for #IREKABITI_FX
Implements RSI, MACD, ATR and other technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

# Optional import for TA-Lib (not available on all platforms)
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    talib = None
    TALIB_AVAILABLE = False

from utils.logger import setup_logger

logger = setup_logger()

class TechnicalAnalysis:
    def __init__(self):
        self.indicators = {}
        
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            rsi = talib.RSI(data['Close'].values, timeperiod=period)
            return pd.Series(rsi, index=data.index, name='RSI')
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(dtype=float)
            
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        try:
            macd, macd_signal, macd_hist = talib.MACD(
                data['Close'].values,
                fastperiod=fast,
                slowperiod=slow,
                signalperiod=signal
            )
            
            return {
                'MACD': pd.Series(macd, index=data.index),
                'Signal': pd.Series(macd_signal, index=data.index),
                'Histogram': pd.Series(macd_hist, index=data.index)
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'MACD': pd.Series(dtype=float), 'Signal': pd.Series(dtype=float), 'Histogram': pd.Series(dtype=float)}
            
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            atr = talib.ATR(
                data['High'].values,
                data['Low'].values,
                data['Close'].values,
                timeperiod=period
            )
            return pd.Series(atr, index=data.index, name='ATR')
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(dtype=float)
            
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            upper, middle, lower = talib.BBANDS(
                data['Close'].values,
                timeperiod=period,
                nbdevup=std,
                nbdevdn=std,
                matype=0
            )
            
            return {
                'Upper': pd.Series(upper, index=data.index),
                'Middle': pd.Series(middle, index=data.index),
                'Lower': pd.Series(lower, index=data.index)
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {'Upper': pd.Series(dtype=float), 'Middle': pd.Series(dtype=float), 'Lower': pd.Series(dtype=float)}
            
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        try:
            slowk, slowd = talib.STOCH(
                data['High'].values,
                data['Low'].values,
                data['Close'].values,
                fastk_period=k_period,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=d_period,
                slowd_matype=0
            )
            
            return {
                'K': pd.Series(slowk, index=data.index),
                'D': pd.Series(slowd, index=data.index)
            }
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return {'K': pd.Series(dtype=float), 'D': pd.Series(dtype=float)}
            
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate various moving averages"""
        try:
            return {
                'SMA_20': talib.SMA(data['Close'].values, timeperiod=20),
                'SMA_50': talib.SMA(data['Close'].values, timeperiod=50),
                'SMA_200': talib.SMA(data['Close'].values, timeperiod=200),
                'EMA_12': talib.EMA(data['Close'].values, timeperiod=12),
                'EMA_26': talib.EMA(data['Close'].values, timeperiod=26),
                'EMA_50': talib.EMA(data['Close'].values, timeperiod=50)
            }
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return {}
            
    def calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, any]:
        """Calculate all technical indicators"""
        try:
            indicators = {}
            
            # RSI
            indicators['RSI'] = self.calculate_rsi(data)
            
            # MACD
            macd_data = self.calculate_macd(data)
            indicators.update(macd_data)
            
            # ATR
            indicators['ATR'] = self.calculate_atr(data)
            
            # Bollinger Bands
            bb_data = self.calculate_bollinger_bands(data)
            indicators.update(bb_data)
            
            # Stochastic
            stoch_data = self.calculate_stochastic(data)
            indicators.update(stoch_data)
            
            # Moving Averages
            ma_data = self.calculate_moving_averages(data)
            indicators.update(ma_data)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return {}
            
    def detect_patterns(self, data: pd.DataFrame) -> Dict[str, bool]:
        """Detect candlestick patterns"""
        try:
            patterns = {}
            
            # Bullish patterns
            patterns['Hammer'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])[-1] > 0
            patterns['Doji'] = talib.CDLDOJI(data['Open'], data['High'], data['Low'], data['Close'])[-1] > 0
            patterns['Engulfing_Bull'] = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])[-1] > 0
            patterns['Morning_Star'] = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])[-1] > 0
            
            # Bearish patterns
            patterns['Shooting_Star'] = talib.CDLSHOOTINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])[-1] < 0
            patterns['Engulfing_Bear'] = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])[-1] < 0
            patterns['Evening_Star'] = talib.CDLEVENINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])[-1] < 0
            patterns['Dark_Cloud'] = talib.CDLDARKCLOUDCOVER(data['Open'], data['High'], data['Low'], data['Close'])[-1] < 0
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}
            
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, any]:
        """Generate trading signals based on technical analysis"""
        try:
            indicators = self.calculate_all_indicators(data)
            patterns = self.detect_patterns(data)
            
            signals = {
                'direction': None,
                'strength': 0,
                'confidence': 0,
                'entry_price': data['Close'].iloc[-1],
                'reasons': []
            }
            
            # Current values
            current_rsi = indicators['RSI'].iloc[-1] if not indicators['RSI'].empty else 50
            current_macd = indicators['MACD'].iloc[-1] if not indicators['MACD'].empty else 0
            macd_signal = indicators['Signal'].iloc[-1] if not indicators['Signal'].empty else 0
            current_price = data['Close'].iloc[-1]
            sma_20 = indicators.get('SMA_20', [np.nan])[-1] if 'SMA_20' in indicators else np.nan
            sma_50 = indicators.get('SMA_50', [np.nan])[-1] if 'SMA_50' in indicators else np.nan
            
            bullish_score = 0
            bearish_score = 0
            
            # RSI Analysis
            if current_rsi < 30:
                bullish_score += 2
                signals['reasons'].append("RSI oversold (bullish)")
            elif current_rsi > 70:
                bearish_score += 2
                signals['reasons'].append("RSI overbought (bearish)")
                
            # MACD Analysis
            if current_macd > macd_signal and not np.isnan(current_macd):
                bullish_score += 1
                signals['reasons'].append("MACD bullish crossover")
            elif current_macd < macd_signal and not np.isnan(current_macd):
                bearish_score += 1
                signals['reasons'].append("MACD bearish crossover")
                
            # Moving Average Analysis
            if not np.isnan(sma_20) and not np.isnan(sma_50):
                if current_price > sma_20 > sma_50:
                    bullish_score += 1
                    signals['reasons'].append("Price above MAs (bullish)")
                elif current_price < sma_20 < sma_50:
                    bearish_score += 1
                    signals['reasons'].append("Price below MAs (bearish)")
                    
            # Pattern Analysis
            bullish_patterns = ['Hammer', 'Engulfing_Bull', 'Morning_Star']
            bearish_patterns = ['Shooting_Star', 'Engulfing_Bear', 'Evening_Star', 'Dark_Cloud']
            
            for pattern in bullish_patterns:
                if patterns.get(pattern, False):
                    bullish_score += 1
                    signals['reasons'].append(f"{pattern} pattern (bullish)")
                    
            for pattern in bearish_patterns:
                if patterns.get(pattern, False):
                    bearish_score += 1
                    signals['reasons'].append(f"{pattern} pattern (bearish)")
                    
            # Determine direction and confidence
            if bullish_score > bearish_score and bullish_score >= 2:
                signals['direction'] = 'BUY'
                signals['strength'] = bullish_score
                signals['confidence'] = min(85, 50 + (bullish_score * 10))
            elif bearish_score > bullish_score and bearish_score >= 2:
                signals['direction'] = 'SELL'
                signals['strength'] = bearish_score
                signals['confidence'] = min(85, 50 + (bearish_score * 10))
            else:
                signals['direction'] = 'HOLD'
                signals['confidence'] = 30
                signals['reasons'].append("Mixed signals - no clear direction")
                
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {'direction': None, 'strength': 0, 'confidence': 0, 'entry_price': 0, 'reasons': []}
            
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        try:
            highs = data['High'].rolling(window=window).max()
            lows = data['Low'].rolling(window=window).min()
            
            resistance = highs.iloc[-1]
            support = lows.iloc[-1]
            
            return {
                'support': support,
                'resistance': resistance,
                'range': resistance - support
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {'support': 0, 'resistance': 0, 'range': 0}
            
    def calculate_volatility(self, data: pd.DataFrame, period: int = 20) -> float:
        """Calculate price volatility"""
        try:
            returns = data['Close'].pct_change().dropna()
            volatility = returns.rolling(window=period).std().iloc[-1] * np.sqrt(252)  # Annualized
            return volatility if not np.isnan(volatility) else 0
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0
            
    def calculate_risk_reward(self, entry_price: float, tp_price: float, sl_price: float) -> Dict[str, float]:
        """Calculate risk/reward ratio"""
        try:
            risk = abs(entry_price - sl_price)
            reward = abs(tp_price - entry_price)
            
            if risk == 0:
                return {'risk': 0, 'reward': 0, 'ratio': 0}
                
            ratio = reward / risk
            
            return {
                'risk': risk,
                'reward': reward,
                'ratio': ratio
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk/reward: {e}")
            return {'risk': 0, 'reward': 0, 'ratio': 0}
