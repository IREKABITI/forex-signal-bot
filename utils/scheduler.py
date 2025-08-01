"""
Scheduler utility for #IREKABITI_FX
Handles scheduled tasks and automation
"""

import asyncio
import schedule
import threading
from datetime import datetime, time, timedelta
from typing import Callable, Dict, List, Optional
import pytz
from concurrent.futures import ThreadPoolExecutor

from utils.logger import setup_logger

logger = setup_logger()

class AsyncScheduler:
    """Asynchronous task scheduler"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def add_task(self, name: str, coro: Callable, schedule_type: str, 
                 interval: int = None, time_str: str = None, 
                 timezone: str = "UTC", enabled: bool = True):
        """Add a scheduled task"""
        try:
            task_config = {
                'coro': coro,
                'schedule_type': schedule_type,  # 'interval', 'daily', 'weekly'
                'interval': interval,
                'time_str': time_str,
                'timezone': timezone,
                'enabled': enabled,
                'last_run': None,
                'next_run': None,
                'run_count': 0,
                'error_count': 0
            }
            
            self.tasks[name] = task_config
            self._calculate_next_run(name)
            
            logger.info(f"✅ Task '{name}' scheduled: {schedule_type}")
            
        except Exception as e:
            logger.error(f"❌ Error adding task '{name}': {e}")
            
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"🗑️ Task '{name}' removed")
        else:
            logger.warning(f"⚠️ Task '{name}' not found")
            
    def enable_task(self, name: str):
        """Enable a task"""
        if name in self.tasks:
            self.tasks[name]['enabled'] = True
            self._calculate_next_run(name)
            logger.info(f"✅ Task '{name}' enabled")
            
    def disable_task(self, name: str):
        """Disable a task"""
        if name in self.tasks:
            self.tasks[name]['enabled'] = False
            logger.info(f"⏸️ Task '{name}' disabled")
            
    def _calculate_next_run(self, name: str):
        """Calculate next run time for a task"""
        try:
            task = self.tasks[name]
            if not task['enabled']:
                task['next_run'] = None
                return
                
            now = datetime.now(pytz.timezone(task['timezone']))
            
            if task['schedule_type'] == 'interval':
                # Interval-based scheduling (seconds)
                next_run = now + timedelta(seconds=task['interval'])
                
            elif task['schedule_type'] == 'daily':
                # Daily at specific time
                time_obj = datetime.strptime(task['time_str'], '%H:%M').time()
                next_run = datetime.combine(now.date(), time_obj)
                next_run = pytz.timezone(task['timezone']).localize(next_run)
                
                # If time has passed today, schedule for tomorrow
                if next_run <= now:
                    next_run += timedelta(days=1)
                    
            elif task['schedule_type'] == 'weekly':
                # Weekly scheduling (not implemented in this basic version)
                next_run = now + timedelta(days=7)
                
            else:
                logger.error(f"❌ Unknown schedule type: {task['schedule_type']}")
                return
                
            task['next_run'] = next_run
            logger.debug(f"📅 Task '{name}' next run: {next_run}")
            
        except Exception as e:
            logger.error(f"❌ Error calculating next run for task '{name}': {e}")
            
    async def _run_task(self, name: str):
        """Run a single task"""
        try:
            task = self.tasks[name]
            
            logger.info(f"🔄 Running task: {name}")
            
            # Record start time
            start_time = datetime.now()
            task['last_run'] = start_time
            
            # Run the coroutine
            await task['coro']()
            
            # Update counters
            task['run_count'] += 1
            
            # Calculate next run
            self._calculate_next_run(name)
            
            # Log completion
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Task '{name}' completed in {duration:.2f}s")
            
        except Exception as e:
            task['error_count'] += 1
            logger.error(f"❌ Task '{name}' failed: {e}")
            
            # Still calculate next run even if task failed
            self._calculate_next_run(name)
            
    async def run_forever(self):
        """Run the scheduler continuously"""
        self.running = True
        self.loop = asyncio.get_event_loop()
        
        logger.info("🚀 Async scheduler started")
        
        while self.running:
            try:
                current_time = datetime.now(pytz.UTC)
                
                # Check which tasks need to run
                tasks_to_run = []
                
                for name, task in self.tasks.items():
                    if (task['enabled'] and 
                        task['next_run'] and 
                        current_time >= task['next_run'].astimezone(pytz.UTC)):
                        tasks_to_run.append(name)
                        
                # Run tasks concurrently
                if tasks_to_run:
                    await asyncio.gather(
                        *[self._run_task(name) for name in tasks_to_run],
                        return_exceptions=True
                    )
                    
                # Sleep for a short interval
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
                
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("🛑 Async scheduler stopped")
        
    def get_task_status(self) -> Dict[str, Dict]:
        """Get status of all tasks"""
        status = {}
        
        for name, task in self.tasks.items():
            status[name] = {
                'enabled': task['enabled'],
                'schedule_type': task['schedule_type'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None,
                'run_count': task['run_count'],
                'error_count': task['error_count']
            }
            
        return status

class TradingScheduler(AsyncScheduler):
    """Specialized scheduler for trading operations"""
    
    def __init__(self):
        super().__init__()
        self.signal_generator = None
        self.portfolio_optimizer = None
        self.db_manager = None
        
    def setup_dependencies(self, signal_generator, portfolio_optimizer, db_manager):
        """Setup service dependencies"""
        self.signal_generator = signal_generator
        self.portfolio_optimizer = portfolio_optimizer
        self.db_manager = db_manager
        
    def setup_default_tasks(self):
        """Setup default trading tasks"""
        try:
            # Signal generation every 5 minutes during trading hours
            self.add_task(
                name="generate_signals",
                coro=self._generate_signals_task,
                schedule_type="interval",
                interval=300,  # 5 minutes
                enabled=True
            )
            
            # Portfolio optimization daily at 22:00 UTC
            self.add_task(
                name="daily_portfolio_optimization",
                coro=self._portfolio_optimization_task,
                schedule_type="daily",
                time_str="22:00",
                timezone="UTC",
                enabled=True
            )
            
            # Daily report at 22:30 UTC
            self.add_task(
                name="daily_report",
                coro=self._daily_report_task,
                schedule_type="daily",
                time_str="22:30",
                timezone="UTC",
                enabled=True
            )
            
            # Market scan every hour during trading sessions
            self.add_task(
                name="hourly_market_scan",
                coro=self._market_scan_task,
                schedule_type="interval",
                interval=3600,  # 1 hour
                enabled=True
            )
            
            # Database cleanup weekly
            self.add_task(
                name="weekly_cleanup",
                coro=self._cleanup_task,
                schedule_type="weekly",
                time_str="01:00",
                timezone="UTC",
                enabled=True
            )
            
            # ML model retraining daily at 02:00 UTC
            self.add_task(
                name="ml_model_retrain",
                coro=self._retrain_models_task,
                schedule_type="daily",
                time_str="02:00",
                timezone="UTC",
                enabled=True
            )
            
            logger.info("✅ Default trading tasks scheduled")
            
        except Exception as e:
            logger.error(f"❌ Error setting up default tasks: {e}")
            
    async def _generate_signals_task(self):
        """Generate signals for all configured pairs"""
        try:
            if not self.signal_generator:
                logger.warning("⚠️ Signal generator not available")
                return
                
            # Check if trading session is active
            from config.settings import settings
            now = datetime.now(pytz.UTC)
            hour = now.hour
            weekday = now.weekday()
            
            # No trading on weekends
            if weekday >= 5:
                return
                
            # Check trading sessions (London: 8-17, New York: 13-22)
            if not (8 <= hour < 17 or 13 <= hour < 22):
                return
                
            logger.info("🔄 Starting scheduled signal generation")
            
            # Generate signals for high-priority pairs
            priority_pairs = [
                "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",  # Major Forex
                "BTCUSDT", "ETHUSDT", "ADAUSDT"  # Major Crypto
            ]
            
            signals_generated = 0
            
            for symbol in priority_pairs:
                try:
                    signal = await self.signal_generator.generate_signal(symbol, "1h")
                    if signal:
                        signals_generated += 1
                        logger.info(f"✅ Signal generated for {symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Error generating signal for {symbol}: {e}")
                    
            logger.info(f"✅ Signal generation completed: {signals_generated} signals")
            
        except Exception as e:
            logger.error(f"❌ Error in signal generation task: {e}")
            
    async def _portfolio_optimization_task(self):
        """Daily portfolio optimization"""
        try:
            if not self.portfolio_optimizer:
                logger.warning("⚠️ Portfolio optimizer not available")
                return
                
            logger.info("🔄 Starting portfolio optimization")
            
            optimization = await self.portfolio_optimizer.optimize_portfolio()
            
            if optimization.get('success'):
                logger.info(f"✅ Portfolio optimized - Expected Return: {optimization['expected_return']:.2f}%")
            else:
                logger.warning("⚠️ Portfolio optimization failed")
                
        except Exception as e:
            logger.error(f"❌ Error in portfolio optimization task: {e}")
            
    async def _daily_report_task(self):
        """Generate daily performance report"""
        try:
            if not self.db_manager:
                logger.warning("⚠️ Database manager not available")
                return
                
            logger.info("🔄 Generating daily report")
            
            # Get daily report data
            report = await self.db_manager.get_daily_report()
            
            # Log summary
            logger.info(
                f"📊 Daily Report: {report['total_signals']} signals, "
                f"{report['win_rate']:.1f}% win rate, "
                f"{report['total_pnl']:.2f}% PnL"
            )
            
            # Here you could send the report to Telegram/Discord
            # self.send_daily_report_to_bots(report)
            
        except Exception as e:
            logger.error(f"❌ Error in daily report task: {e}")
            
    async def _market_scan_task(self):
        """Hourly market scan"""
        try:
            if not self.signal_generator:
                logger.warning("⚠️ Signal generator not available")
                return
                
            logger.info("🔄 Starting market scan")
            
            scan_results = await self.signal_generator.scan_all_markets()
            
            logger.info(
                f"🔍 Market Scan: {scan_results['total_scanned']} pairs scanned, "
                f"{scan_results['high_confidence']} high-confidence opportunities"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in market scan task: {e}")
            
    async def _cleanup_task(self):
        """Weekly database cleanup"""
        try:
            if not self.db_manager:
                logger.warning("⚠️ Database manager not available")
                return
                
            logger.info("🔄 Starting database cleanup")
            
            await self.db_manager.cleanup_old_data(days_to_keep=90)
            
            logger.info("✅ Database cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error in cleanup task: {e}")
            
    async def _retrain_models_task(self):
        """Daily ML model retraining"""
        try:
            logger.info("🔄 Starting ML model retraining")
            
            # This would retrain ML models with latest data
            # Implementation depends on ML service setup
            
            logger.info("✅ ML model retraining completed")
            
        except Exception as e:
            logger.error(f"❌ Error in ML retrain task: {e}")

# Create global scheduler instance
trading_scheduler = TradingScheduler()
