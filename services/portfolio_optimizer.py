"""
Portfolio Optimization Service for #IREKABITI_FX
Implements Modern Portfolio Theory and risk management
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from services.market_data import MarketDataService
from database.db_manager import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger()

class PortfolioOptimizer:
    def __init__(self):
        self.market_data = MarketDataService()
        self.db_manager = DatabaseManager()
        
    async def get_returns_data(self, symbols: List[str], period_days: int = 252) -> pd.DataFrame:
        """Get historical returns data for symbols"""
        try:
            returns_data = {}
            
            for symbol in symbols:
                # Determine market type
                market_type = "crypto" if symbol.endswith("USDT") else "forex"
                
                # Get historical data
                data = await self.market_data.get_market_data(symbol, "1d", market_type)
                
                if data is not None and len(data) > period_days:
                    # Calculate daily returns
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns.tail(period_days)
                    
            if not returns_data:
                return pd.DataFrame()
                
            # Combine into DataFrame
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            return returns_df
            
        except Exception as e:
            logger.error(f"Error getting returns data: {e}")
            return pd.DataFrame()
            
    def calculate_portfolio_metrics(self, returns: pd.DataFrame, weights: np.array) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        try:
            if returns.empty or len(weights) != len(returns.columns):
                return {}
                
            # Portfolio returns
            portfolio_returns = (returns * weights).sum(axis=1)
            
            # Annualized metrics
            annual_return = portfolio_returns.mean() * 252
            annual_volatility = portfolio_returns.std() * np.sqrt(252)
            
            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(portfolio_returns, 5)
            
            # Sortino ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252)
            sortino_ratio = (annual_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            return {
                'annual_return': annual_return,
                'annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'calmar_ratio': annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
            
    def optimize_portfolio_sharpe(self, returns: pd.DataFrame, target_risk: float = None) -> Dict[str, any]:
        """Optimize portfolio for maximum Sharpe ratio"""
        try:
            if returns.empty:
                return {}
                
            n_assets = len(returns.columns)
            
            # Calculate expected returns and covariance matrix
            expected_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252
            
            # Objective function: negative Sharpe ratio
            def negative_sharpe(weights):
                portfolio_return = np.sum(expected_returns * weights)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                if portfolio_volatility == 0:
                    return -float('inf')
                    
                sharpe_ratio = (portfolio_return - 0.02) / portfolio_volatility
                return -sharpe_ratio
                
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            # Add target risk constraint if specified
            if target_risk:
                constraints.append({
                    'type': 'eq',
                    'fun': lambda x: np.sqrt(np.dot(x.T, np.dot(cov_matrix, x))) - target_risk
                })
                
            # Bounds (0% to 40% allocation per asset)
            bounds = tuple((0, 0.4) for _ in range(n_assets))
            
            # Initial guess (equal weights)
            initial_guess = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                negative_sharpe,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate metrics
                metrics = self.calculate_portfolio_metrics(returns, optimal_weights)
                
                return {
                    'weights': dict(zip(returns.columns, optimal_weights)),
                    'metrics': metrics,
                    'optimization_success': True
                }
            else:
                logger.error(f"Portfolio optimization failed: {result.message}")
                return {'optimization_success': False}
                
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return {}
            
    def optimize_portfolio_risk_parity(self, returns: pd.DataFrame) -> Dict[str, any]:
        """Optimize portfolio using risk parity approach"""
        try:
            if returns.empty:
                return {}
                
            n_assets = len(returns.columns)
            cov_matrix = returns.cov() * 252
            
            # Risk parity objective: minimize sum of squared risk contributions
            def risk_parity_objective(weights):
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                if portfolio_volatility == 0:
                    return float('inf')
                    
                # Risk contributions
                marginal_contrib = np.dot(cov_matrix, weights) / portfolio_volatility
                contrib = weights * marginal_contrib
                
                # Target equal risk contribution
                target_contrib = portfolio_volatility / n_assets
                
                return np.sum((contrib - target_contrib) ** 2)
                
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            ]
            
            # Bounds
            bounds = tuple((0.01, 0.5) for _ in range(n_assets))
            
            # Initial guess
            initial_guess = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                risk_parity_objective,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = result.x
                metrics = self.calculate_portfolio_metrics(returns, optimal_weights)
                
                return {
                    'weights': dict(zip(returns.columns, optimal_weights)),
                    'metrics': metrics,
                    'optimization_success': True
                }
            else:
                return {'optimization_success': False}
                
        except Exception as e:
            logger.error(f"Error in risk parity optimization: {e}")
            return {}
            
    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix of returns"""
        try:
            return returns.corr()
        except Exception as e:
            logger.error(f"Error calculating correlation matrix: {e}")
            return pd.DataFrame()
            
    def monte_carlo_simulation(self, returns: pd.DataFrame, weights: np.array, 
                             days: int = 252, simulations: int = 1000) -> Dict[str, any]:
        """Run Monte Carlo simulation for portfolio"""
        try:
            if returns.empty:
                return {}
                
            # Portfolio statistics
            portfolio_returns = (returns * weights).sum(axis=1)
            daily_mean = portfolio_returns.mean()
            daily_std = portfolio_returns.std()
            
            # Run simulations
            simulation_results = []
            
            for _ in range(simulations):
                # Generate random returns
                random_returns = np.random.normal(daily_mean, daily_std, days)
                
                # Calculate cumulative return
                cumulative_return = np.prod(1 + random_returns) - 1
                simulation_results.append(cumulative_return)
                
            simulation_results = np.array(simulation_results)
            
            # Calculate statistics
            expected_return = np.mean(simulation_results)
            volatility = np.std(simulation_results)
            
            # Confidence intervals
            percentiles = [5, 25, 50, 75, 95]
            confidence_intervals = {
                f"p{p}": np.percentile(simulation_results, p)
                for p in percentiles
            }
            
            # Probability of positive return
            prob_positive = np.sum(simulation_results > 0) / simulations
            
            return {
                'expected_return': expected_return,
                'volatility': volatility,
                'confidence_intervals': confidence_intervals,
                'probability_positive': prob_positive,
                'simulations_count': simulations,
                'time_horizon_days': days
            }
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {}
            
    async def optimize_portfolio(self, symbols: List[str] = None) -> Dict[str, any]:
        """Main portfolio optimization function"""
        try:
            # Use default symbols if none provided
            if not symbols:
                symbols = [
                    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",  # Forex
                    "BTCUSDT", "ETHUSDT", "ADAUSDT"  # Crypto
                ]
                
            logger.info(f"Optimizing portfolio for symbols: {symbols}")
            
            # Get returns data
            returns = await self.get_returns_data(symbols, period_days=252)
            
            if returns.empty:
                logger.error("No returns data available for optimization")
                return {
                    'success': False,
                    'error': 'No returns data available'
                }
                
            # Run different optimization strategies
            sharpe_optimization = self.optimize_portfolio_sharpe(returns)
            risk_parity_optimization = self.optimize_portfolio_risk_parity(returns)
            
            # Calculate correlation matrix
            correlation_matrix = self.calculate_correlation_matrix(returns)
            
            # Choose best optimization based on Sharpe ratio
            if (sharpe_optimization.get('optimization_success', False) and 
                risk_parity_optimization.get('optimization_success', False)):
                
                sharpe_ratio_sharpe = sharpe_optimization['metrics'].get('sharpe_ratio', 0)
                sharpe_ratio_rp = risk_parity_optimization['metrics'].get('sharpe_ratio', 0)
                
                if sharpe_ratio_sharpe >= sharpe_ratio_rp:
                    best_optimization = sharpe_optimization
                    strategy = "Maximum Sharpe Ratio"
                else:
                    best_optimization = risk_parity_optimization
                    strategy = "Risk Parity"
                    
            elif sharpe_optimization.get('optimization_success', False):
                best_optimization = sharpe_optimization
                strategy = "Maximum Sharpe Ratio"
            elif risk_parity_optimization.get('optimization_success', False):
                best_optimization = risk_parity_optimization
                strategy = "Risk Parity"
            else:
                return {
                    'success': False,
                    'error': 'All optimization strategies failed'
                }
                
            # Run Monte Carlo simulation with optimal weights
            weights_array = np.array([best_optimization['weights'][symbol] for symbol in returns.columns])
            monte_carlo_results = self.monte_carlo_simulation(returns, weights_array)
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(best_optimization['metrics'])
            
            return {
                'success': True,
                'strategy': strategy,
                'weights': best_optimization['weights'],
                'expected_return': best_optimization['metrics']['annual_return'] * 100,
                'volatility': best_optimization['metrics']['annual_volatility'] * 100,
                'sharpe_ratio': best_optimization['metrics']['sharpe_ratio'],
                'max_drawdown': best_optimization['metrics']['max_drawdown'] * 100,
                'risk_score': risk_score,
                'correlation_matrix': correlation_matrix.to_dict(),
                'monte_carlo': monte_carlo_results,
                'optimization_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def calculate_risk_score(self, metrics: Dict[str, float]) -> int:
        """Calculate risk score from 1-100"""
        try:
            # Factors contributing to risk score
            volatility = metrics.get('annual_volatility', 0)
            max_drawdown = abs(metrics.get('max_drawdown', 0))
            sharpe_ratio = metrics.get('sharpe_ratio', 0)
            
            # Base score starts at 50
            risk_score = 50
            
            # Adjust based on volatility (0-50% vol range)
            if volatility > 0.3:  # High volatility
                risk_score += 30
            elif volatility > 0.2:  # Medium volatility
                risk_score += 20
            elif volatility > 0.1:  # Low volatility
                risk_score += 10
                
            # Adjust based on max drawdown
            if max_drawdown > 0.3:  # High drawdown
                risk_score += 20
            elif max_drawdown > 0.2:  # Medium drawdown
                risk_score += 10
                
            # Adjust based on Sharpe ratio (negative adjustment for good Sharpe)
            if sharpe_ratio > 1.5:  # Excellent Sharpe
                risk_score -= 20
            elif sharpe_ratio > 1.0:  # Good Sharpe
                risk_score -= 10
            elif sharpe_ratio < 0:  # Poor Sharpe
                risk_score += 15
                
            # Ensure score is within bounds
            return max(1, min(100, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50
            
    async def get_position_sizing(self, symbol: str, account_balance: float, 
                                risk_percent: float = 2.0, stop_loss_pips: float = None) -> Dict[str, float]:
        """Calculate position sizing based on risk management"""
        try:
            # Get current price and ATR for volatility
            market_type = "crypto" if symbol.endswith("USDT") else "forex"
            current_price = await self.market_data.get_current_price(symbol, market_type)
            
            if not current_price:
                return {}
                
            # Get ATR for stop loss calculation if not provided
            if stop_loss_pips is None:
                data = await self.market_data.get_market_data(symbol, "1h", market_type)
                if data is not None and len(data) > 14:
                    atr = data['High'].subtract(data['Low']).rolling(14).mean().iloc[-1]
                    stop_loss_pips = atr * 2  # 2x ATR stop loss
                else:
                    stop_loss_pips = current_price * 0.02  # 2% default stop loss
                    
            # Calculate position size
            risk_amount = account_balance * (risk_percent / 100)
            
            # Position size = Risk Amount / Stop Loss Distance
            if market_type == "forex":
                # For forex, assume standard lot = 100,000 units
                pip_value = 10  # USD per pip for standard lot
                position_size_lots = risk_amount / (stop_loss_pips * pip_value)
                
                return {
                    'position_size_lots': position_size_lots,
                    'position_size_units': position_size_lots * 100000,
                    'risk_amount': risk_amount,
                    'stop_loss_distance': stop_loss_pips,
                    'position_value': position_size_lots * 100000 * current_price
                }
            else:
                # For crypto
                position_size_units = risk_amount / stop_loss_pips
                
                return {
                    'position_size_units': position_size_units,
                    'risk_amount': risk_amount,
                    'stop_loss_distance': stop_loss_pips,
                    'position_value': position_size_units * current_price
                }
                
        except Exception as e:
            logger.error(f"Error calculating position sizing for {symbol}: {e}")
            return {}
