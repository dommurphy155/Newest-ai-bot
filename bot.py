#!/usr/bin/env python3
"""
Telegram Bot Handler for AI Trading Bot
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import os
import logging
import asyncio
from typing import Optional
from datetime import datetime

import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError, NetworkError, RetryAfter

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, token: str, chat_id: str, trader=None):
        self.token = token
        self.chat_id = chat_id
        self.trader = trader
        self.app = None
        self.running = False
        
        # Initialize bot with error handling
        try:
            self.bot = telegram.Bot(token=self.token)
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise

    async def start_command(self, update, context):
        """Handle /start command"""
        try:
            await update.message.reply_text(
                "🤖 AI Trading Bot Started!\n\n"
                "Available commands:\n"
                "/start - Start the bot\n"
                "/status - Check bot status\n"
                "/balance - Check account balance\n"
                "/stop - Stop the bot\n"
                "/help - Show this help message"
            )
            logger.info("Start command executed")
        except Exception as e:
            logger.error(f"Error in start command: {e}")

    async def status_command(self, update, context):
        """Handle /status command"""
        try:
            status_msg = f"🟢 Bot Status: {'Running' if self.running else 'Stopped'}\n"
            status_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if self.trader:
                status_msg += f"📊 Trader: {'Active' if self.trader.running else 'Inactive'}\n"
            
            await update.message.reply_text(status_msg)
            logger.info("Status command executed")
        except Exception as e:
            logger.error(f"Error in status command: {e}")

    async def balance_command(self, update, context):
        """Handle /balance command"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            balance = await self.trader.get_balance()
            if balance is not None:
                await update.message.reply_text(f"💰 Account Balance: ${balance:.2f}")
            else:
                await update.message.reply_text("❌ Failed to retrieve balance")
            
            logger.info("Balance command executed")
        except Exception as e:
            logger.error(f"Error in balance command: {e}")
            await update.message.reply_text("❌ Error retrieving balance")

    async def stop_command(self, update, context):
        """Handle /stop command"""
        try:
            await update.message.reply_text("🛑 Stopping bot...")
            self.running = False
            if self.trader:
                self.trader.stop()
            logger.info("Stop command executed")
        except Exception as e:
            logger.error(f"Error in stop command: {e}")

    async def help_command(self, update, context):
        """Handle /help command"""
        try:
            help_text = (
                "🤖 AI Trading Bot Help\n\n"
                "Commands:\n"
                "/start - Start the bot\n"
                "/status - Check bot status\n"
                "/balance - Check account balance\n"
                "/stop - Stop the bot\n"
                "/help - Show this help message\n\n"
                "The bot automatically analyzes market conditions and executes trades based on AI predictions."
            )
            await update.message.reply_text(help_text)
            logger.info("Help command executed")
        except Exception as e:
            logger.error(f"Error in help command: {e}")

    async def handle_message(self, update, context):
        """Handle regular messages"""
        try:
            message_text = update.message.text
            logger.info(f"Received message: {message_text}")
            
            # Simple response for now
            await update.message.reply_text("I'm an AI trading bot. Use /help to see available commands.")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error: {context.error}")
        
        if isinstance(context.error, RetryAfter):
            logger.warning(f"Rate limited. Waiting {context.error.retry_after} seconds")
            await asyncio.sleep(context.error.retry_after)
        elif isinstance(context.error, NetworkError):
            logger.error("Network error occurred")
        else:
            logger.error(f"Unexpected error: {context.error}")

    async def send_message(self, text: str):
        """Send message to chat"""
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text)
            logger.info("Message sent successfully")
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")

    async def send_report(self, report: str):
        """Send trading report"""
        try:
            formatted_report = f"📊 Trading Report\n\n{report}"
            await self.send_message(formatted_report)
        except Exception as e:
            logger.error(f"Error sending report: {e}")

    async def run(self):
        """Run the bot"""
        try:
            self.running = True
            logger.info("Starting Telegram bot...")
            
            # Build application
            self.app = ApplicationBuilder().token(self.token).build()
            
            # Add handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("balance", self.balance_command))
            self.app.add_handler(CommandHandler("stop", self.stop_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            self.app.add_error_handler(self.error_handler)
            
            logger.info("Bot handlers registered")
            
            # Send startup message
            await self.send_message("🚀 AI Trading Bot started successfully!")
            
            # Run polling
            await self.app.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            self.running = False
            raise

    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.app:
            self.app.stop()
        logger.info("Bot stopped")

# Legacy function for backward compatibility
def run_bot():
    """Legacy function - not used in new architecture"""
    logger.warning("run_bot() is deprecated. Use TradingBot class instead.")
    pass
