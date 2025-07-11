#!/usr/bin/env python3
"""
Production-Ready AI Trading Bot Main Entry Point
Optimized for Maximum Profit Generation
"""

import os
import sys
import asyncio
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Ensure Python 3.8+ compatibility
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required. Current version:", sys.version)
    sys.exit(1)

# Create directories before logging setup
Path("logs").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Setup logging after ensuring directories exist
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from config import config
    from bot import EnhancedTradingBot
    from trader import AdvancedTrader
    from scraper import EnhancedNewsScraper
    from database import Database
    from technical_analysis import TechnicalAnalyzer
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)

class TradingBotManager:
    """Production-ready trading bot manager with memory optimization"""
    
    def __init__(self):
        self.trader = None
        self.bot = None
        self.scraper = None
        self.db = None
        self.analyzer = None
        self.running = False
        
    async def cleanup_old_data(self):
        """Clean up old data to save storage and memory"""
        try:
            cutoff_date = datetime.now() - timedelta(days=3.5)
            
            if self.db:
                # Clean old news data
                await self.db.execute(
                    "DELETE FROM news_sentiment WHERE timestamp < ?", 
                    (cutoff_date,)
                )
                
                # Clean old trade data older than 30 days
                old_trades_cutoff = datetime.now() - timedelta(days=30)
                await self.db.execute(
                    "DELETE FROM trades WHERE timestamp < ?", 
                    (old_trades_cutoff,)
                )
                
                # Vacuum database to reclaim space
                await self.db.execute("VACUUM")
                
            # Clean old log files
            logs_dir = Path("logs")
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        
            logger.info(f"🧹 Cleaned data older than {cutoff_date}")
            
        except Exception as e:
            logger.error(f"Error cleaning old data: {e}")
        
    async def initialize_components(self):
        """Initialize all trading bot components"""
        try:
            logger.info("🚀 Initializing AI Trading Bot v3.0...")
            
            # Initialize database
            self.db = Database(config.database.db_path)
            await self.db.initialize()
            logger.info("✅ Database initialized")
            
            # Initialize technical analyzer
            self.analyzer = TechnicalAnalyzer()
            logger.info("✅ Technical analyzer ready")
            
            # Initialize news scraper
            self.scraper = EnhancedNewsScraper()
            logger.info("✅ News scraper initialized")
            
            # Initialize trader
            self.trader = AdvancedTrader(
                api_key=config.api.oanda_api_key,
                account_id=config.api.oanda_account_id,
                scraper=self.scraper
            )
            logger.info("✅ Advanced trader ready")
            
            # Initialize Telegram bot
            self.bot = EnhancedTradingBot(
                token=config.api.telegram_bot_token,
                chat_id=config.api.telegram_chat_id,
                trader=self.trader
            )
            logger.info("✅ Enhanced Telegram bot ready")
            
            # Clean old data on startup
            await self.cleanup_old_data()
            
            logger.info("🎯 All components initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def start_trading(self):
        """Start the trading system"""
        try:
            self.running = True
            logger.info("🔥 Starting AI Trading Bot v3.0 - MAXIMUM PROFIT MODE")
            
            # Start all components concurrently
            tasks = [
                asyncio.create_task(self.trader.run()),
                asyncio.create_task(self.bot.run()),
                asyncio.create_task(self.scraper.continuous_monitoring()),
                asyncio.create_task(self.health_monitor()),
                asyncio.create_task(self.cleanup_scheduler())
            ]
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Trading system error: {e}")
            await self.shutdown()
    
    async def cleanup_scheduler(self):
        """Schedule regular cleanup to maintain low memory usage"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Clean every hour
                await self.cleanup_old_data()
            except Exception as e:
                logger.error(f"Cleanup scheduler error: {e}")
                await asyncio.sleep(3600)
    
    async def health_monitor(self):
        """Monitor system health and performance"""
        while self.running:
            try:
                # Check component health
                if not self.trader.running:
                    logger.warning("⚠️ Trader stopped, attempting restart...")
                    asyncio.create_task(self.trader.run())
                
                # Log performance metrics
                if self.trader and hasattr(self.trader, 'trade_count'):
                    balance = await self.trader.get_balance()
                    logger.info(f"💰 Balance: ${balance:.2f} | Trades: {self.trader.trade_count}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            logger.info("🛑 Shutting down trading system...")
            self.running = False
            
            if self.trader:
                self.trader.stop()
            if self.bot:
                self.bot.stop()
            if self.scraper:
                self.scraper.stop()
                
            logger.info("✅ Shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    if hasattr(signal_handler, 'manager'):
        asyncio.create_task(signal_handler.manager.shutdown())

async def main():
    """Main entry point"""
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and run bot manager
        manager = TradingBotManager()
        signal_handler.manager = manager
        
        # Initialize components
        if not await manager.initialize_components():
            logger.error("❌ Failed to initialize components")
            return 1
        
        # Start trading
        await manager.start_trading()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        return 0
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        return 1

if __name__ == "__main__":
    # Run the bot
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

