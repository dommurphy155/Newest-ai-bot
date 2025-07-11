#!/usr/bin/env python3
"""
AI Trading Bot - Enhanced Main Entry Point
Compatible with Python 3.8+ and Ubuntu 20.04
High-frequency trading with advanced ML models
"""

import os
import sys
import logging
import asyncio
import signal
from datetime import datetime
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging.log_file),
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
        """Comprehensive environment validation using config."""
        try:
            config._validate()
            logger.info("Environment validation passed")
            return True
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return False

    async def initialize_components(self):
        """Initialize all bot components."""
        try:
            from bot import TradingBot
            from trader import AdvancedTrader
            from scraper import EnhancedNewsScraper
            # Initialize components
            self.components['scraper'] = EnhancedNewsScraper()
            self.components['trader'] = AdvancedTrader(
                api_key=config.api.oanda_api_key,
                account_id=config.api.oanda_account_id,
                scraper=self.components['scraper']
            )
            self.components['bot'] = TradingBot(
                token=config.api.telegram_bot_token,
                chat_id=config.api.telegram_chat_id,
                trader=self.components['trader']
            )
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False

    async def start_components(self):
        """Start all components concurrently."""
        try:
            tasks = [
                self.components['bot'].run(),
                self.components['trader'].run(),
                self.monitor_performance()
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Component startup failed: {e}")
            raise

    async def monitor_performance(self):
        """Monitor and optimize performance."""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                trader_status = await self.components['trader'].get_detailed_status()
                self.performance_metrics.update({
                    'total_trades': trader_status.get('trade_count', 0),
                    'total_profit': trader_status.get('total_pnl', 0.0),
                    'win_rate': trader_status.get('win_rate', 0.0)
                })
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    def signal_handler(self, signum, frame):
        """Graceful shutdown handler for pm2 and CLI."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                component.stop()
        sys.exit(0)

    async def run(self):
        """Main execution method."""
        try:
            self.running = True
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            if not self.check_environment():
                sys.exit(1)
            if not await self.initialize_components():
                sys.exit(1)
            logger.info("🚀 Starting AI Trading Bot (production-ready)")
            await self.start_components()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

async def main():
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