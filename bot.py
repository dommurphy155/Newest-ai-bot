import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if BOT_TOKEN is None or CHAT_ID is None:
    logger.error('TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables are required.')
    exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🤖 AI Trading Bot Online.\n'
        'Commands:\n'
        '/status - Show bot status\n'
        '/whatyoudoin - Current activities\n'
        '/help - This message'
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Connect to shared state for real status
    await update.message.reply_text('🟢 Bot is running. No open trades.')


async def whatyoudoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Return current bot activities and diagnostics
    await update.message.reply_text('Working hard scanning markets and trading...')


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('whatyoudoin', whatyoudoin))

    app.run_polling()


if __name__ == '__main__':
    main()