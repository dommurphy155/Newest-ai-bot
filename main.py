import os
import asyncio
import logging
from bot import main as bot_main
from trader import Trader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv('HF_TOKEN')
OANDA_API_KEY = os.getenv('OANDA_API_KEY')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')

if not all([HF_TOKEN, OANDA_API_KEY, OANDA_ACCOUNT_ID]):
    logger.error('HF_TOKEN, OANDA_API_KEY, and OANDA_ACCOUNT_ID environment variables must be set.')
    exit(1)

async def run_trader():
    trader = Trader(
        api_key=OANDA_API_KEY,
        account_id=OANDA_ACCOUNT_ID,
        hf_token=HF_TOKEN
    )
    await trader.run()

def main():
    loop = asyncio.get_event_loop()
    # Run bot in background thread
    loop.run_in_executor(None, bot_main)
    # Run trading loop
    loop.run_until_complete(run_trader())

if __name__ == '__main__':
    main()