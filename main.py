print("staring main.py")
from bot import run main.py
#!/usr/bin/env python3
<<<<<<< HEAD
AI Trading Bot - Main Entry Point
=======
"""
AI Trading Bot - Enhanced Main Entry Point
>>>>>>> 882435ae4b6e5432be719c1c26c2a5f930b9b94f
Compatible with Python 3.8+ and Ubuntu 20.04
High-frequency trading with advanced ML models
"""

import os
import sys
import logging
import asyncio
import signal
from datetime import datetime
from typing import Optional, Dict, Any

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.FileHandler('logs/trades.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.components = {}
        self.running = False
        self.performance_metrics = {
            'start_time': datetime.now(),
            'total_trades': 0,
            'profitable_trades': 0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0
        }

    def check_environment(self) -> bool:
        """Comprehensive environment validation"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
            'OANDA_API_KEY', 'OANDA_ACCOUNT_ID'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            logger.error(f"Missing environment variables: {missing}")
            return False
        
        # Validate environment values
        if len(os.getenv('TELEGRAM_BOT_TOKEN', '')) < 20:
            logger.error("Invalid TELEGRAM_BOT_TOKEN")
            return False
        
        logger.info("Environment validation passed")
        return True

    async def initialize_components(self):
        """Initialize all bot components"""
        try:
            from bot import TradingBot
            from trader import AdvancedTrader
            from scraper import EnhancedNewsScraper
            from send_report import ReportSender
            
            # Initialize components
            self.components['scraper'] = EnhancedNewsScraper()
            self.components['trader'] = AdvancedTrader(
                api_key=os.getenv('OANDA_API_KEY'),
                account_id=os.getenv('OANDA_ACCOUNT_ID'),
                scraper=self.components['scraper']
            )
            self.components['bot'] = TradingBot(
                token=os.getenv('TELEGRAM_BOT_TOKEN'),
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                trader=self.components['trader']
            )
            self.components['reporter'] = ReportSender()
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False

    async def start_components(self):
        """Start all components concurrently"""
        try:
            tasks = [
                self.components['bot'].run(),
                self.components['trader'].run(),
                self.monitor_performance()
            ]
            
            await self.components['reporter'].send_startup_message()
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Component startup failed: {e}")
            raise

    async def monitor_performance(self):
        """Monitor and optimize performance"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get current metrics
                trader_status = await self.components['trader'].get_detailed_status()
                
                # Update performance metrics
                self.performance_metrics.update({
                    'total_trades': trader_status.get('trade_count', 0),
                    'total_profit': trader_status.get('total_pnl', 0.0),
                    'win_rate': trader_status.get('win_rate', 0.0)
                })
                
                # Send performance report every hour
                current_time = datetime.now()
                if current_time.minute == 0:
                    await self.send_performance_report()
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def send_performance_report(self):
        """Send hourly performance report"""
        try:
            report_data = {
                'performance': self.performance_metrics,
                **await self.components['trader'].get_detailed_status()
            }
            
            await self.components['reporter'].send_trading_report(report_data)
            
        except Exception as e:
            logger.error(f"Performance report error: {e}")

    def signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
        
        # Stop all components
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                component.stop()
        
        sys.exit(0)

    async def run(self):
        """Main execution method"""
        try:
            self.running = True
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Validate environment
            if not self.check_environment():
                sys.exit(1)
            
            # Initialize components
            if not await self.initialize_components():
                sys.exit(1)
            
            logger.info("🚀 Starting AI Trading Bot with advanced features")
            
            # Start all components
            await self.start_components()
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

async def main():
    """Main async entry point"""
    manager = BotManager()
    await manager.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)