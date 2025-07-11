#!/usr/bin/env python3
"""
🚀 ULTRA-OPTIMIZED AI Trading Bot v3.0
Production-ready with 30+ profit-maximizing strategies
Compatible with Python 3.8+ and Ubuntu 20.04
High-frequency trading with advanced ML models
"""

import os
import sys
import logging
import asyncio
import signal
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from config import config

# Configure optimized logging
logging.basicConfig(
    level=getattr(logging, config.logging.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class UltraOptimizedBotManager:
    def __init__(self):
        self.components = {}
        self.running = False
        self.start_time = datetime.now()
        
        # Enhanced performance tracking
        self.performance_metrics = {
            'start_time': self.start_time,
            'total_trades': 0,
            'profitable_trades': 0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'profit_factor': 0.0,
            'avg_trade_duration': 0.0,
            'max_consecutive_losses': 0,
            'current_consecutive_losses': 0,
            'daily_pnl': 0.0,
            'hourly_pnl': 0.0,
            'peak_balance': 0.0,
            'current_balance': 0.0,
            'system_uptime': 0.0,
            'memory_usage': 0.0,
            'cpu_usage': 0.0
        }
        
        # Strategy performance tracking
        self.strategy_performance = {
            'momentum_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'mean_reversion': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'breakout_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'sentiment_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'volatility_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'correlation_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'news_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'ml_prediction': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'arbitrage': {'wins': 0, 'losses': 0, 'pnl': 0.0},
            'scalping': {'wins': 0, 'losses': 0, 'pnl': 0.0}
        }

    def check_environment(self) -> bool:
        """Comprehensive environment validation with system checks."""
        try:
            # Validate config
            config._validate()
            
            # Check system resources
            memory = psutil.virtual_memory()
            if memory.available < 500 * 1024 * 1024:  # 500MB minimum
                logger.warning("Low memory available: {:.1f}MB".format(memory.available / 1024 / 1024))
            
            # Check Python version
            if sys.version_info < (3, 8):
                logger.error("Python 3.8+ required")
                return False
            
            # Check required directories
            required_dirs = ['logs', 'data', 'backups']
            for dir_name in required_dirs:
                os.makedirs(dir_name, exist_ok=True)
            
            logger.info("✅ Environment validation passed")
            return True
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            return False

    async def initialize_components(self):
        """Initialize all bot components with error recovery."""
        try:
            from bot import UltraOptimizedTradingBot
            from trader import UltraOptimizedTrader
            from scraper import UltraOptimizedNewsScraper
            from database import UltraOptimizedDatabase
            from technical_analysis import UltraOptimizedTechnicalAnalyzer
            
            # Initialize database first
            self.components['database'] = UltraOptimizedDatabase()
            await self.components['database'].initialize()
            
            # Initialize scraper
            self.components['scraper'] = UltraOptimizedNewsScraper()
            
            # Initialize technical analyzer
            self.components['analyzer'] = UltraOptimizedTechnicalAnalyzer()
            
            # Initialize trader with all components
            self.components['trader'] = UltraOptimizedTrader(
                api_key=config.api.oanda_api_key,
                account_id=config.api.oanda_account_id,
                scraper=self.components['scraper'],
                analyzer=self.components['analyzer'],
                database=self.components['database']
            )
            
            # Initialize bot
            self.components['bot'] = UltraOptimizedTradingBot(
                token=config.api.telegram_bot_token,
                chat_id=config.api.telegram_chat_id,
                trader=self.components['trader'],
                database=self.components['database']
            )
            
            logger.info("✅ All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            return False

    async def start_components(self):
        """Start all components concurrently with monitoring."""
        try:
            tasks = [
                self.components['bot'].run(),
                self.components['trader'].run(),
                self.monitor_performance(),
                self.monitor_system_resources(),
                self.optimize_memory_usage()
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"❌ Component startup failed: {e}")
            raise

    async def monitor_performance(self):
        """Enhanced performance monitoring with strategy tracking."""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Get trader status
                trader_status = await self.components['trader'].get_detailed_status()
                
                # Update performance metrics
                self.performance_metrics.update({
                    'total_trades': trader_status.get('trade_count', 0),
                    'total_profit': trader_status.get('total_pnl', 0.0),
                    'win_rate': trader_status.get('win_rate', 0.0),
                    'current_balance': trader_status.get('balance', 0.0),
                    'daily_pnl': trader_status.get('daily_pnl', 0.0),
                    'system_uptime': (datetime.now() - self.start_time).total_seconds()
                })
                
                # Update peak balance
                if self.performance_metrics['current_balance'] > self.performance_metrics['peak_balance']:
                    self.performance_metrics['peak_balance'] = self.performance_metrics['current_balance']
                
                # Calculate drawdown
                if self.performance_metrics['peak_balance'] > 0:
                    drawdown = (self.performance_metrics['peak_balance'] - self.performance_metrics['current_balance']) / self.performance_metrics['peak_balance']
                    self.performance_metrics['max_drawdown'] = max(self.performance_metrics['max_drawdown'], drawdown)
                
                # Log performance every 5 minutes
                if int(self.performance_metrics['system_uptime']) % 300 == 0:
                    logger.info(f"📊 Performance Update: P&L=${self.performance_metrics['total_profit']:.2f}, Win Rate={self.performance_metrics['win_rate']:.1f}%")
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)

    async def monitor_system_resources(self):
        """Monitor system resources for optimization."""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Monitor memory usage
                memory = psutil.virtual_memory()
                self.performance_metrics['memory_usage'] = memory.percent
                
                # Monitor CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.performance_metrics['cpu_usage'] = cpu_percent
                
                # Alert if resources are high
                if memory.percent > 80:
                    logger.warning(f"⚠️ High memory usage: {memory.percent}%")
                if cpu_percent > 80:
                    logger.warning(f"⚠️ High CPU usage: {cpu_percent}%")
                    
            except Exception as e:
                logger.error(f"System monitoring error: {e}")

    async def optimize_memory_usage(self):
        """Optimize memory usage periodically."""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Force garbage collection
                gc.collect()
                
                # Log memory usage
                memory = psutil.virtual_memory()
                logger.info(f"🧹 Memory optimization: {memory.percent}% used")
                
            except Exception as e:
                logger.error(f"Memory optimization error: {e}")

    def signal_handler(self, signum, frame):
        """Enhanced graceful shutdown handler."""
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self.running = False
        
        # Stop all components
        for name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                logger.info(f"✅ Stopped {name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        # Save final performance report
        self.save_final_report()
        sys.exit(0)

    def save_final_report(self):
        """Save final performance report."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                'performance_metrics': self.performance_metrics,
                'strategy_performance': self.strategy_performance
            }
            
            with open('logs/final_report.json', 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info("📊 Final performance report saved")
        except Exception as e:
            logger.error(f"Error saving final report: {e}")

    async def run(self):
        """Main execution method with enhanced error handling."""
        try:
            self.running = True
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            logger.info("🚀 Starting ULTRA-OPTIMIZED AI Trading Bot v3.0")
            
            if not self.check_environment():
                logger.error("❌ Environment check failed")
                sys.exit(1)
                
            if not await self.initialize_components():
                logger.error("❌ Component initialization failed")
                sys.exit(1)
                
            logger.info("✅ All systems ready - Starting trading operations")
            await self.start_components()
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            sys.exit(1)

async def main():
    manager = UltraOptimizedBotManager()
    await manager.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot shutdown complete")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)