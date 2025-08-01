"""
Discord Bot for #IREKABITI_FX
"""

import discord
from discord.ext import commands
from datetime import datetime
from config.settings import settings
from services.signal_generator import SignalGenerator
from services.portfolio_optimizer import PortfolioOptimizer
from database.db_manager import DatabaseManager
from utils.charts import ChartGenerator
from utils.logger import setup_logger

logger = setup_logger()

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.signal_generator = SignalGenerator()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.db_manager = DatabaseManager()
        self.chart_generator = ChartGenerator()
        
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f"🎮 Discord Bot logged in as {self.user}")
        await self.change_presence(activity=discord.Game(name="#IREKABITI_FX Trading Signals"))
        
    @commands.command(name='signals')
    async def signals_command(self, ctx):
        """Get latest trading signals"""
        try:
            signals = await self.signal_generator.get_latest_signals()
            
            if not signals:
                embed = discord.Embed(
                    title="🔍 No Signals Available",
                    description="Markets are being analyzed...",
                    color=0xffaa00
                )
                await ctx.send(embed=embed)
                return
                
            embed = discord.Embed(
                title="📊 #IREKABITI_FX Latest Signals",
                color=0x00ff00
            )
            
            for i, signal in enumerate(signals[:3], 1):
                confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⚡" if signal['confidence'] >= 75 else "📈"
                risk_emoji = "🟢" if signal['risk_percent'] <= 1 else "🟡" if signal['risk_percent'] <= 1.5 else "🔴"
                
                embed.add_field(
                    name=f"{confidence_emoji} {signal['symbol']} - {signal['direction']}",
                    value=f"📈 Entry: {signal['entry_price']}\n"
                          f"🎯 TP: {signal['tp_price']}\n"
                          f"🛡️ SL: {signal['sl_price']}\n"
                          f"💎 Confidence: {signal['confidence']}/100\n"
                          f"{risk_emoji} Risk: {signal['risk_percent']:.1f}%",
                    inline=True
                )
                
            embed.set_footer(text=f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in Discord signals command: {e}")
            await ctx.send("❌ Error retrieving signals. Please try again later.")
            
    @commands.command(name='scan')
    async def scan_command(self, ctx):
        """Admin-only market scan command"""
        if ctx.author.id not in settings.ADMIN_DISCORD_IDS:
            await ctx.send("🔒 This command is only available to administrators.")
            return
            
        try:
            await ctx.send("🔍 Scanning markets... This may take a moment.")
            
            scan_results = await self.signal_generator.scan_all_markets()
            
            embed = discord.Embed(
                title="🔍 Market Scan Results",
                color=0x0099ff
            )
            
            embed.add_field(
                name="📊 Market Overview",
                value=f"Forex Opportunities: {scan_results['forex_count']}\n"
                      f"Crypto Opportunities: {scan_results['crypto_count']}\n"
                      f"High Confidence Signals: {scan_results['high_confidence']}",
                inline=False
            )
            
            if scan_results['top_signals']:
                top_signals = "\n".join([
                    f"• {signal['symbol']} - {signal['confidence']}/100"
                    for signal in scan_results['top_signals'][:3]
                ])
                embed.add_field(
                    name="🔥 Top Opportunities",
                    value=top_signals,
                    inline=False
                )
                
            embed.set_footer(text=f"⏰ Scan Time: {datetime.now().strftime('%H:%M:%S UTC')}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in Discord scan command: {e}")
            await ctx.send("❌ Error scanning markets. Please try again later.")
            
    @commands.command(name='report')
    async def report_command(self, ctx):
        """Daily performance report"""
        try:
            report_data = await self.db_manager.get_daily_report()
            
            embed = discord.Embed(
                title="📈 #IREKABITI_FX Daily Report",
                color=0x00ff00
            )
            
            embed.add_field(
                name="📊 Performance Metrics",
                value=f"Signals Generated: {report_data['total_signals']}\n"
                      f"Successful Signals: {report_data['successful_signals']}\n"
                      f"Win Rate: {report_data['win_rate']:.1f}%\n"
                      f"Total PnL: {report_data['total_pnl']:.2f}%",
                inline=True
            )
            
            embed.add_field(
                name="📈 Analytics",
                value=f"Average Confidence: {report_data['avg_confidence']:.1f}\n"
                      f"Best Performer: {report_data['best_signal']}\n"
                      f"Active Pairs: {report_data['active_pairs']}",
                inline=True
            )
            
            embed.set_footer(text=f"🕐 Report Time: {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}")
            
            # Try to attach equity curve chart
            chart_buffer = await self.chart_generator.generate_equity_curve()
            if chart_buffer:
                file = discord.File(chart_buffer, filename="equity_curve.png")
                embed.set_image(url="attachment://equity_curve.png")
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in Discord report command: {e}")
            await ctx.send("❌ Error generating report. Please try again later.")
            
    @commands.command(name='stats')
    async def stats_command(self, ctx):
        """Trading statistics"""
        try:
            stats = await self.db_manager.get_trading_stats()
            
            embed = discord.Embed(
                title="📊 #IREKABITI_FX Statistics",
                color=0x9932cc
            )
            
            embed.add_field(
                name="📈 Overall Performance",
                value=f"Total Signals: {stats['total_signals']}\n"
                      f"Win Rate: {stats['win_rate']:.1f}%\n"
                      f"Total Return: {stats['total_return']:.2f}%\n"
                      f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Risk Metrics",
                value=f"Max Drawdown: {stats['max_drawdown']:.2f}%\n"
                      f"Best Signal: {stats['best_signal']:.2f}%\n"
                      f"Active Days: {stats['active_days']}\n"
                      f"Avg Confidence: {stats['avg_confidence']:.1f}",
                inline=True
            )
            
            top_pairs = "\n".join([
                f"• {pair}: {performance:.1f}%"
                for pair, performance in list(stats['top_pairs'].items())[:5]
            ])
            
            embed.add_field(
                name="🏆 Top Performing Pairs",
                value=top_pairs,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in Discord stats command: {e}")
            await ctx.send("❌ Error retrieving statistics. Please try again later.")
            
    @commands.command(name='optimize')
    async def optimize_command(self, ctx):
        """Portfolio optimization command"""
        if ctx.author.id not in settings.ADMIN_DISCORD_IDS:
            await ctx.send("🔒 This command is only available to administrators.")
            return
            
        try:
            await ctx.send("🧮 Optimizing portfolio... Please wait.")
            
            optimization = await self.portfolio_optimizer.optimize_portfolio()
            
            embed = discord.Embed(
                title="🧮 Portfolio Optimization Results",
                color=0xff6600
            )
            
            embed.add_field(
                name="📈 Expected Performance",
                value=f"Expected Return: {optimization['expected_return']:.2f}%\n"
                      f"Volatility: {optimization['volatility']:.2f}%\n"
                      f"Sharpe Ratio: {optimization['sharpe_ratio']:.2f}\n"
                      f"Risk Score: {optimization['risk_score']}/100",
                inline=False
            )
            
            allocations = "\n".join([
                f"• {asset}: {weight:.1f}%"
                for asset, weight in optimization['weights'].items()
            ])
            
            embed.add_field(
                name="💼 Recommended Allocation",
                value=allocations,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in Discord optimize command: {e}")
            await ctx.send("❌ Error optimizing portfolio. Please try again later.")
            
    async def send_signal_notification(self, signal):
        """Send signal notification to Discord channels"""
        try:
            embed = discord.Embed(
                title="🚨 #IREKABITI_FX Signal Alert",
                color=0xff0000 if signal['direction'] == 'SELL' else 0x00ff00
            )
            
            confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⚡" if signal['confidence'] >= 75 else "📈"
            risk_emoji = "🟢" if signal['risk_percent'] <= 1 else "🟡" if signal['risk_percent'] <= 1.5 else "🔴"
            
            embed.add_field(
                name=f"{confidence_emoji} {signal['symbol']} - {signal['direction']}",
                value=f"📈 Entry: {signal['entry_price']}\n"
                      f"🎯 TP: {signal['tp_price']}\n"
                      f"🛡️ SL: {signal['sl_price']}\n"
                      f"💎 Confidence: {signal['confidence']}/100\n"
                      f"{risk_emoji} Risk: {signal['risk_percent']:.1f}%",
                inline=False
            )
            
            embed.add_field(
                name="📝 Analysis",
                value=signal['analysis'],
                inline=False
            )
            
            embed.set_footer(text=f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}")
            
            # Get all subscribed channels from database
            channels = await self.db_manager.get_subscribed_channels('discord')
            
            for channel_id in channels:
                try:
                    channel = self.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error sending signal to channel {channel_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending Discord signal notification: {e}")
            
    async def start(self):
        """Start the Discord bot"""
        try:
            await self.start(settings.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
