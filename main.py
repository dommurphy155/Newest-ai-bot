print("staring main.py")
from bot import run main.py
#!/usr/bin/env python3
"""
AI Trading Bot - Main Entry Point
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import os
import sys
import logging
import asyncio
import signal
from typing import Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'OANDA_API_KEY',
        'OANDA_ACCOUNT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please export the following variables:")
        for var in missing_vars:
            logger.error(f"export {var}=your_value")
        sys.exit(1)
    
    logger.info("All required environment variables are set")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

async def main():
    """Main async function to run the bot"""
    try:
        # Check environment variables
        check_environment()
        
        # Import modules after environment check
        from bot import TradingBot
        from trader import Trader
        
        # Get credentials
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        api_key = os.getenv('OANDA_API_KEY')
        account_id = os.getenv('OANDA_ACCOUNT_ID')
        hf_token = os.getenv('HF_TOKEN')  # Optional
        
        logger.info("Initializing AI Trading Bot...")
        
        # Initialize components
        trader = Trader(api_key=api_key, account_id=account_id, hf_token=hf_token)
        bot = TradingBot(token=bot_token, chat_id=chat_id, trader=trader)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting bot components...")
        
        # Run bot and trader concurrently
        await asyncio.gather(
            bot.run(),
            trader.run()
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
