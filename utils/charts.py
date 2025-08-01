"""
Chart generation utilities for #IREKABITI_FX
Creates visualizations for signals, performance, and analytics
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import seaborn as sns

from database.db_manager import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger()

class ChartGenerator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # Set style
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
        # Configure matplotlib for better performance
        plt.rcParams['figure.facecolor'] = '#1a1a1a'
        plt.rcParams['axes.facecolor'] = '#2d2d2d'
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        
    async def generate_equity_curve(self, days: int = 30) -> Optional[io.BytesIO]:
        """Generate equity curve chart"""
        try:
            # Get portfolio data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get signals for the period
            signals = await self.db_manager.get_signals_in_range(start_date, end_date)
            
            if not signals:
                return None
                
            # Calculate cumulative returns
            dates = []
            cumulative_pnl = []
            running_total = 0
            
            for signal in signals:
                if signal.timestamp:
                    dates.append(signal.timestamp)
                    # Simulate PnL (in real implementation, use actual results)
                    pnl = np.random.normal(0.5, 2.0)  # Average 0.5% return with 2% volatility
                    running_total += pnl
                    cumulative_pnl.append(running_total)
                    
            if not dates:
                return None
                
            # Create DataFrame
            df = pd.DataFrame({
                'date': dates,
                'cumulative_pnl': cumulative_pnl
            })
            df = df.sort_values('date')
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot equity curve
            ax.plot(df['date'], df['cumulative_pnl'], 
                   color='#00ff88', linewidth=2, label='Equity Curve')
            
            # Add zero line
            ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            
            # Formatting
            ax.set_title('#IREKABITI_FX Equity Curve', fontsize=16, fontweight='bold', color='white')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Cumulative PnL (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
            plt.xticks(rotation=45)
            
            # Add statistics text
            stats_text = f"Total Return: {cumulative_pnl[-1]:.2f}%\n"
            stats_text += f"Max Drawdown: {min(cumulative_pnl):.2f}%\n"
            stats_text += f"Signals: {len(signals)}"
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', 
                   facecolor='black', alpha=0.8), fontsize=10)
            
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating equity curve: {e}")
            return None
            
    async def generate_performance_chart(self, days: int = 30) -> Optional[io.BytesIO]:
        """Generate performance analytics chart"""
        try:
            # Get trading stats
            stats = await self.db_manager.get_trading_stats()
            
            if not stats or stats['total_signals'] == 0:
                return None
                
            # Create subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. Win/Loss Pie Chart
            win_count = int(stats['total_signals'] * stats['win_rate'] / 100)
            loss_count = stats['total_signals'] - win_count
            
            ax1.pie([win_count, loss_count], 
                   labels=['Wins', 'Losses'], 
                   colors=['#00ff88', '#ff4444'],
                   autopct='%1.1f%%',
                   startangle=90)
            ax1.set_title('Win/Loss Distribution', fontsize=14, fontweight='bold')
            
            # 2. Top Performing Pairs
            if stats['top_pairs']:
                pairs = list(stats['top_pairs'].keys())[:5]
                performance = list(stats['top_pairs'].values())[:5]
                
                bars = ax2.bar(pairs, performance, color='#00ff88' if all(p >= 0 for p in performance) else ['#00ff88' if p >= 0 else '#ff4444' for p in performance])
                ax2.set_title('Top Performing Pairs', fontsize=14, fontweight='bold')
                ax2.set_ylabel('Average PnL (%)')
                ax2.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, value in zip(bars, performance):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.1f}%', ha='center', va='bottom')
                           
            # 3. Monthly Performance (simulated)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            monthly_returns = np.random.normal(2, 5, 6)  # Simulated monthly returns
            
            colors = ['#00ff88' if r >= 0 else '#ff4444' for r in monthly_returns]
            ax3.bar(months, monthly_returns, color=colors)
            ax3.set_title('Monthly Performance', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Monthly Return (%)')
            ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
            
            # 4. Risk Metrics
            metrics = ['Win Rate', 'Sharpe Ratio', 'Max DD', 'Avg Confidence']
            values = [
                stats['win_rate'],
                stats['sharpe_ratio'] * 20,  # Scale for visibility
                abs(stats['max_drawdown']),
                stats['avg_confidence']
            ]
            
            ax4.barh(metrics, values, color=['#00ff88', '#ffaa00', '#ff4444', '#0088ff'])
            ax4.set_title('Risk Metrics', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Value')
            
            # Add value labels
            for i, value in enumerate(values):
                ax4.text(value + 1, i, f'{value:.1f}', va='center')
                
            plt.suptitle('#IREKABITI_FX Performance Analytics', 
                        fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#1a1a1a', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating performance chart: {e}")
            return None
            
    def generate_signal_chart(self, symbol: str, data: pd.DataFrame, 
                            signal: Dict[str, Any]) -> Optional[io.BytesIO]:
        """Generate signal analysis chart"""
        try:
            if data.empty:
                return None
                
            # Create subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), 
                                               gridspec_kw={'height_ratios': [3, 1, 1]})
            
            # 1. Price chart with signal
            ax1.plot(data.index, data['Close'], color='white', linewidth=1, label='Price')
            
            # Add moving averages if available
            if len(data) >= 20:
                ma20 = data['Close'].rolling(20).mean()
                ax1.plot(data.index, ma20, color='#ffaa00', linewidth=1, alpha=0.7, label='MA20')
                
            # Mark signal entry point
            entry_price = signal.get('entry_price', data['Close'].iloc[-1])
            tp_price = signal.get('tp_price', entry_price * 1.02)
            sl_price = signal.get('sl_price', entry_price * 0.98)
            
            # Signal arrow
            direction = signal.get('direction', 'BUY')
            arrow_color = '#00ff88' if direction == 'BUY' else '#ff4444'
            
            ax1.annotate(f'{direction}\n{entry_price:.5f}', 
                        xy=(data.index[-1], entry_price),
                        xytext=(data.index[-5], entry_price),
                        arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2),
                        fontsize=10, fontweight='bold', color=arrow_color,
                        ha='center')
            
            # TP and SL lines
            ax1.axhline(y=tp_price, color='#00ff88', linestyle='--', alpha=0.7, label='TP')
            ax1.axhline(y=sl_price, color='#ff4444', linestyle='--', alpha=0.7, label='SL')
            
            ax1.set_title(f'{symbol} - {direction} Signal (Confidence: {signal.get("confidence", 0)}%)', 
                         fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. Volume
            if 'Volume' in data.columns:
                ax2.bar(data.index, data['Volume'], color='#666666', alpha=0.7)
                ax2.set_title('Volume', fontsize=12)
                ax2.grid(True, alpha=0.3)
                
            # 3. RSI (if available)
            try:
                import talib
                rsi = talib.RSI(data['Close'].values, timeperiod=14)
                ax3.plot(data.index, rsi, color='#0088ff', linewidth=1)
                ax3.axhline(y=70, color='#ff4444', linestyle='--', alpha=0.5)
                ax3.axhline(y=30, color='#00ff88', linestyle='--', alpha=0.5)
                ax3.set_title('RSI(14)', fontsize=12)
                ax3.set_ylim(0, 100)
                ax3.grid(True, alpha=0.3)
                
            except ImportError:
                ax3.text(0.5, 0.5, 'TA-Lib not available', 
                        transform=ax3.transAxes, ha='center', va='center')
                
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#1a1a1a', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating signal chart: {e}")
            return None
            
    async def generate_correlation_heatmap(self, symbols: List[str]) -> Optional[io.BytesIO]:
        """Generate correlation heatmap for symbols"""
        try:
            from services.market_data import MarketDataService
            
            market_data = MarketDataService()
            returns_data = {}
            
            # Get returns data for each symbol
            for symbol in symbols:
                market_type = "crypto" if symbol.endswith("USDT") else "forex"
                data = await market_data.get_market_data(symbol, "1d", market_type)
                
                if data is not None and len(data) > 30:
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns.tail(30)  # Last 30 days
                    
            if len(returns_data) < 2:
                return None
                
            # Create DataFrame and calculate correlation
            df = pd.DataFrame(returns_data).dropna()
            correlation_matrix = df.corr()
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 8))
            
            sns.heatmap(correlation_matrix, 
                       annot=True, 
                       cmap='RdYlBu_r', 
                       center=0, 
                       square=True,
                       fmt='.2f',
                       cbar_kws={'label': 'Correlation'},
                       ax=ax)
            
            ax.set_title('Asset Correlation Matrix (30-day)', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#1a1a1a', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating correlation heatmap: {e}")
            return None
            
    def generate_risk_distribution_chart(self, portfolio_data: Dict[str, Any]) -> Optional[io.BytesIO]:
        """Generate risk distribution chart"""
        try:
            if 'weights' not in portfolio_data:
                return None
                
            weights = portfolio_data['weights']
            symbols = list(weights.keys())
            allocations = list(weights.values())
            
            # Create pie chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Portfolio allocation pie chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
            wedges, texts, autotexts = ax1.pie(allocations, 
                                              labels=symbols, 
                                              autopct='%1.1f%%',
                                              colors=colors,
                                              startangle=90)
            
            ax1.set_title('Portfolio Allocation', fontsize=14, fontweight='bold')
            
            # Risk metrics bar chart
            risk_metrics = ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
            risk_values = [
                portfolio_data.get('expected_return', 0),
                portfolio_data.get('volatility', 0),
                portfolio_data.get('sharpe_ratio', 0) * 10,  # Scale for visibility
                abs(portfolio_data.get('max_drawdown', 0))
            ]
            
            colors = ['#00ff88', '#ffaa00', '#0088ff', '#ff4444']
            bars = ax2.bar(risk_metrics, risk_values, color=colors)
            
            ax2.set_title('Risk Metrics', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Value (%)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, risk_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.1f}%', ha='center', va='bottom')
                        
            plt.suptitle('#IREKABITI_FX Portfolio Risk Analysis', 
                        fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='#1a1a1a', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating risk distribution chart: {e}")
            return None
            
    def create_chart_base64(self, chart_buffer: io.BytesIO) -> str:
        """Convert chart buffer to base64 string for web display"""
        try:
            if chart_buffer:
                chart_buffer.seek(0)
                chart_base64 = base64.b64encode(chart_buffer.read()).decode()
                return f"data:image/png;base64,{chart_base64}"
            return ""
            
        except Exception as e:
            logger.error(f"Error converting chart to base64: {e}")
            return ""
