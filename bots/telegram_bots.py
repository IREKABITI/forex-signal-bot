"""
Telegram Bot for #IREKABITI_FX
"""

import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import settings
from services.signal_generator import SignalGenerator
from services.portfolio_optimizer import PortfolioOptimizer
from database.db_manager import DatabaseManager
from utils.charts import ChartGenerator
from utils.logger import setup_logger
import io

logger = setup_logger()

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
        self.signal_generator = SignalGenerator()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.db_manager = DatabaseManager()
        self.chart_generator = ChartGenerator()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("signals", self.signals_command))
        self.app.add_handler(CommandHandler("scan", self.scan_command))
        self.app.add_handler(CommandHandler("report", self.report_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CommandHandler("optimize", self.optimize_command))
        self.app.add_handler(CommandHandler("settings", self.settings_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_text = """
🚀 **Welcome to #IREKABITI_FX**
*AI-Powered Multi-Market Trading Ecosystem*

📊 **Available Commands:**
• `/signals` - Get latest trading signals
• `/scan` - Scan markets for opportunities
• `/report` - Daily performance report
• `/stats` - Trading statistics
• `/optimize` - Portfolio optimization
• `/settings` - Bot settings

🤖 **Features:**
✅ Real-time Forex & Crypto signals
✅ ML-powered pattern recognition
✅ Sentiment analysis integration
✅ Risk management tools
✅ Portfolio optimization
✅ Advanced analytics

💎 Elite trading signals with confidence scoring!
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Latest Signals", callback_data="latest_signals")],
            [InlineKeyboardButton("📈 Market Scan", callback_data="market_scan")],
            [InlineKeyboardButton("📱 Mobile App", url="https://app.irekabiti-fx.com")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get latest trading signals"""
        try:
            signals = await self.signal_generator.get_latest_signals()
            
            if not signals:
                await update.message.reply_text("🔍 No signals available at the moment. Markets are being analyzed...")
                return
                
            message = "📊 **#IREKABITI_FX Latest Signals**\n\n"
            
            for signal in signals[:5]:  # Show top 5 signals
                confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⚡" if signal['confidence'] >= 75 else "📈"
                risk_emoji = "🟢" if signal['risk_percent'] <= 1 else "🟡" if signal['risk_percent'] <= 1.5 else "🔴"
                
                message += f"{confidence_emoji} **{signal['symbol']}** - {signal['direction']}\n"
                message += f"📈 **Entry:** {signal['entry_price']}\n"
                message += f"🎯 **TP:** {signal['tp_price']}\n"
                message += f"🛡️ **SL:** {signal['sl_price']}\n"
                message += f"💎 **Confidence:** {signal['confidence']}/100\n"
                message += f"{risk_emoji} **Risk:** {signal['risk_percent']:.1f}%\n"
                message += f"⏰ **Time:** {signal['timestamp']}\n"
                message += f"📝 **Reason:** {signal['analysis']}\n\n"
                
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in signals command: {e}")
            await update.message.reply_text("❌ Error retrieving signals. Please try again later.")
            
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin-only market scan command"""
        if update.effective_user.id not in settings.ADMIN_TELEGRAM_IDS:
            await update.message.reply_text("🔒 This command is only available to administrators.")
            return
            
        try:
            await update.message.reply_text("🔍 Scanning markets... This may take a moment.")
            
            scan_results = await self.signal_generator.scan_all_markets()
            
            message = "🔍 **Market Scan Results**\n\n"
            message += f"📊 **Forex Opportunities:** {scan_results['forex_count']}\n"
            message += f"💰 **Crypto Opportunities:** {scan_results['crypto_count']}\n"
            message += f"⭐ **High Confidence Signals:** {scan_results['high_confidence']}\n"
            message += f"⏰ **Scan Time:** {datetime.now().strftime('%H:%M:%S UTC')}\n\n"
            
            if scan_results['top_signals']:
                message += "🔥 **Top Opportunities:**\n"
                for signal in scan_results['top_signals'][:3]:
                    message += f"• {signal['symbol']} - {signal['confidence']}/100\n"
                    
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in scan command: {e}")
            await update.message.reply_text("❌ Error scanning markets. Please try again later.")
            
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Daily performance report"""
        try:
            report_data = await self.db_manager.get_daily_report()
            
            message = "📈 **#IREKABITI_FX Daily Report**\n\n"
            message += f"📊 **Signals Generated:** {report_data['total_signals']}\n"
            message += f"✅ **Successful Signals:** {report_data['successful_signals']}\n"
            message += f"📈 **Win Rate:** {report_data['win_rate']:.1f}%\n"
            message += f"💰 **Total PnL:** {report_data['total_pnl']:.2f}%\n"
            message += f"📊 **Average Confidence:** {report_data['avg_confidence']:.1f}\n"
            message += f"⚡ **Best Performer:** {report_data['best_signal']}\n"
            message += f"🕐 **Report Time:** {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}"
            
            # Generate equity curve chart
            chart_buffer = await self.chart_generator.generate_equity_curve()
            if chart_buffer:
                await update.message.reply_photo(
                    photo=chart_buffer,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in report command: {e}")
            await update.message.reply_text("❌ Error generating report. Please try again later.")
            
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trading statistics"""
        try:
            stats = await self.db_manager.get_trading_stats()
            
            message = "📊 **#IREKABITI_FX Statistics**\n\n"
            message += f"📈 **Total Signals:** {stats['total_signals']}\n"
            message += f"✅ **Win Rate:** {stats['win_rate']:.1f}%\n"
            message += f"💰 **Total Return:** {stats['total_return']:.2f}%\n"
            message += f"📊 **Sharpe Ratio:** {stats['sharpe_ratio']:.2f}\n"
            message += f"📉 **Max Drawdown:** {stats['max_drawdown']:.2f}%\n"
            message += f"⭐ **Best Signal:** {stats['best_signal']:.2f}%\n"
            message += f"📅 **Active Days:** {stats['active_days']}\n"
            message += f"🔥 **Avg Confidence:** {stats['avg_confidence']:.1f}\n\n"
            
            message += "🏆 **Top Performing Pairs:**\n"
            for pair, performance in stats['top_pairs'].items():
                message += f"• {pair}: {performance:.1f}%\n"
                
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text("❌ Error retrieving statistics. Please try again later.")
            
    async def optimize_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Portfolio optimization command"""
        if update.effective_user.id not in settings.ADMIN_TELEGRAM_IDS:
            await update.message.reply_text("🔒 This command is only available to administrators.")
            return
            
        try:
            await update.message.reply_text("🧮 Optimizing portfolio... Please wait.")
            
            optimization = await self.portfolio_optimizer.optimize_portfolio()
            
            message = "🧮 **Portfolio Optimization Results**\n\n"
            message += f"📈 **Expected Return:** {optimization['expected_return']:.2f}%\n"
            message += f"📊 **Volatility:** {optimization['volatility']:.2f}%\n"
            message += f"⚡ **Sharpe Ratio:** {optimization['sharpe_ratio']:.2f}\n\n"
            
            message += "💼 **Recommended Allocation:**\n"
            for asset, weight in optimization['weights'].items():
                message += f"• {asset}: {weight:.1f}%\n"
                
            message += f"\n🎯 **Risk Score:** {optimization['risk_score']}/100"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in optimize command: {e}")
            await update.message.reply_text("❌ Error optimizing portfolio. Please try again later.")
            
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot settings"""
        if update.effective_user.id not in settings.ADMIN_TELEGRAM_IDS:
            await update.message.reply_text("🔒 This command is only available to administrators.")
            return
            
        keyboard = [
            [InlineKeyboardButton("⚙️ Risk Settings", callback_data="risk_settings")],
            [InlineKeyboardButton("📊 Signal Settings", callback_data="signal_settings")],
            [InlineKeyboardButton("🕐 Time Settings", callback_data="time_settings")],
            [InlineKeyboardButton("📱 Notification Settings", callback_data="notification_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "⚙️ **#IREKABITI_FX Settings**\n\nSelect a category to configure:"
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "latest_signals":
            await self.signals_command(update, context)
        elif query.data == "market_scan":
            await self.scan_command(update, context)
        # Add more callback handlers as needed
        
    async def send_signal_notification(self, signal):
        """Send signal notification to all users"""
        try:
            confidence_emoji = "🔥" if signal['confidence'] >= 85 else "⚡" if signal['confidence'] >= 75 else "📈"
            risk_emoji = "🟢" if signal['risk_percent'] <= 1 else "🟡" if signal['risk_percent'] <= 1.5 else "🔴"
            
            message = f"🚨 **#IREKABITI_FX Signal Alert**\n\n"
            message += f"{confidence_emoji} **{signal['symbol']}** - {signal['direction']}\n"
            message += f"📈 **Entry:** {signal['entry_price']}\n"
            message += f"🎯 **TP:** {signal['tp_price']}\n"
            message += f"🛡️ **SL:** {signal['sl_price']}\n"
            message += f"💎 **Confidence:** {signal['confidence']}/100\n"
            message += f"{risk_emoji} **Risk:** {signal['risk_percent']:.1f}%\n"
            message += f"📝 **Analysis:** {signal['analysis']}"
            
            # Get all subscribed users from database
            users = await self.db_manager.get_subscribed_users('telegram')
            
            for user_id in users:
                try:
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending signal to user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")
            
    async def start(self):
        """Start the Telegram bot"""
        try:
            await self.app.initialize()
            await self.app.start()
            logger.info("📱 #IREKABITI_FX Telegram Bot started")
            await self.app.updater.start_polling()
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
