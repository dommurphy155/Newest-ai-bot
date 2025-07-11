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
from datetime import datetime
from pathlib import Path

# Ensure Python 3.8+ compatibility
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required. Current version:", sys.version)
    sys.exit(1)

# Setup logging before imports
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
    """Production-ready trading bot manager"""
    
    def __init__(self):
        self.trader = None
        self.bot = None
        self.scraper = None
        self.db = None
        self.analyzer = None
        self.running = False
        
    async def initialize_components(self):
        """Initialize all trading bot components"""
        try:
            logger.info("🚀 Initializing AI Trading Bot v3.0...")
            
            # Create directories
            Path("logs").mkdir(exist_ok=True)
            Path("data").mkdir(exist_ok=True)
            
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
                asyncio.create_task(self.health_monitor())
            ]
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Trading system error: {e}")
            await self.shutdown()
    
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
    # Check environment variables
    required_vars = [
        'OANDA_API_KEY', 'OANDA_ACCOUNT_ID', 
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run the bot
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

