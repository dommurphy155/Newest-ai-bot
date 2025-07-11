#!/usr/bin/env python3
"""
Enhanced Telegram Bot Handler for AI Trading Bot
Production-ready with advanced features and error handling
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

try:
    import telegram
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    from telegram.error import TelegramError, NetworkError, RetryAfter
except ImportError as e:
    logging.error(f"Telegram imports failed: {e}")
    raise

logger = logging.getLogger(__name__)

class EnhancedTradingBot:
    def __init__(self, token: str, chat_id: str, trader=None):
        self.token = token
        self.chat_id = chat_id
        self.trader = trader
        self.app = None
        self.running = False
        self.start_time = datetime.now()
        self.message_count = 0
        self.last_heartbeat = datetime.now()
        
        # Performance tracking
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'daily_pnl': 0.0
        }
        
        try:
            self.bot = telegram.Bot(token=self.token)
            logger.info("Enhanced Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise

    async def start_command(self, update, context):
        """Enhanced /start command with system info"""
        try:
            uptime = datetime.now() - self.start_time
            status_msg = (
                "🚀 <b>AI Trading Bot v2.0 - ACTIVE</b>\n\n"
                f"⏰ <b>Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"📊 <b>Status:</b> {'🟢 Running' if self.running else '🔴 Stopped'}\n"
                f"💼 <b>Trader:</b> {'🟢 Active' if self.trader and self.trader.running else '🔴 Inactive'}\n\n"
                "<b>Available Commands:</b>\n"
                "/start - System status\n"
                "/status - Detailed status\n"
                "/balance - Account balance\n"
                "/performance - Trading performance\n"
                "/positions - Open positions\n"
                "/profit - P&L summary\n"
                "/risk - Risk management\n"
                "/stop - Emergency stop\n"
                "/restart - Restart trading\n"
                "/help - Command help"
            )
            
            await update.message.reply_text(status_msg, parse_mode='HTML')
            self.message_count += 1
            logger.info("Enhanced start command executed")
        except Exception as e:
            logger.error(f"Error in start command: {e}")

    async def status_command(self, update, context):
        """Enhanced /status command with detailed metrics"""
        try:
            uptime = datetime.now() - self.start_time
            
            # Get trader status
            trader_status = {}
            if self.trader:
                trader_status = await self.trader.get_status()
            
            status_msg = (
                "📊 <b>SYSTEM STATUS REPORT</b>\n\n"
                f"🕒 <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏱️ <b>Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"🤖 <b>Bot Status:</b> {'🟢 Active' if self.running else '🔴 Inactive'}\n"
                f"📈 <b>Trader Status:</b> {'🟢 Trading' if trader_status.get('running') else '🔴 Stopped'}\n"
                f"💬 <b>Messages:</b> {self.message_count}\n"
                f"🔄 <b>Heartbeat:</b> {(datetime.now() - self.last_heartbeat).seconds}s ago\n\n"
                f"📊 <b>Performance:</b>\n"
                f"• Total Trades: {self.performance['total_trades']}\n"
                f"• Win Rate: {(self.performance['winning_trades']/max(self.performance['total_trades'],1)*100):.1f}%\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}"
            )
            
            await update.message.reply_text(status_msg, parse_mode='HTML')
            self.last_heartbeat = datetime.now()
            logger.info("Enhanced status command executed")
        except Exception as e:
            logger.error(f"Error in status command: {e}")

    async def balance_command(self, update, context):
        """Enhanced /balance command with account details"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            balance = await self.trader.get_balance()
            account_info = await self.trader.get_account_info()
            
            if balance is None:
                await update.message.reply_text("❌ Failed to retrieve balance")
                return
            
            margin_used = float(account_info.get('marginUsed', 0)) if account_info else 0
            margin_available = float(account_info.get('marginAvailable', 0)) if account_info else 0
            
            balance_msg = (
                "💰 <b>ACCOUNT BALANCE</b>\n\n"
                f"💵 <b>Balance:</b> ${balance:.2f}\n"
                f"📊 <b>Margin Used:</b> ${margin_used:.2f}\n"
                f"📈 <b>Margin Available:</b> ${margin_available:.2f}\n"
                f"🎯 <b>Margin Level:</b> {((balance/max(margin_used,1))*100):.1f}%\n\n"
                f"📊 <b>Today's Performance:</b>\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}\n"
                f"• Best Trade: ${self.performance['best_trade']:.2f}\n"
                f"• Worst Trade: ${self.performance['worst_trade']:.2f}"
            )
            
            await update.message.reply_text(balance_msg, parse_mode='HTML')
            logger.info("Enhanced balance command executed")
        except Exception as e:
            logger.error(f"Error in balance command: {e}")

    async def performance_command(self, update, context):
        """New /performance command for detailed metrics"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            win_rate = (self.performance['winning_trades'] / max(self.performance['total_trades'], 1)) * 100
            avg_trade = self.performance['total_pnl'] / max(self.performance['total_trades'], 1)
            
            perf_msg = (
                "🎯 <b>TRADING PERFORMANCE</b>\n\n"
                f"📈 <b>Total Trades:</b> {self.performance['total_trades']}\n"
                f"🏆 <b>Winning Trades:</b> {self.performance['winning_trades']}\n"
                f"📊 <b>Win Rate:</b> {win_rate:.1f}%\n"
                f"💰 <b>Total P&L:</b> ${self.performance['total_pnl']:.2f}\n"
                f"📊 <b>Average Trade:</b> ${avg_trade:.2f}\n"
                f"🚀 <b>Best Trade:</b> ${self.performance['best_trade']:.2f}\n"
                f"⚠️ <b>Worst Trade:</b> ${self.performance['worst_trade']:.2f}\n"
                f"📅 <b>Daily P&L:</b> ${self.performance['daily_pnl']:.2f}"
            )
            
            await update.message.reply_text(perf_msg, parse_mode='HTML')
            logger.info("Performance command executed")
        except Exception as e:
            logger.error(f"Error in performance command: {e}")

    async def positions_command(self, update, context):
        """New /positions command for open positions"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            positions = await self.trader.get_open_positions()
            
            if not positions:
                await update.message.reply_text("📊 No open positions")
                return
            
            pos_msg = "📊 <b>OPEN POSITIONS</b>\n\n"
            
            for pos in positions:
                if float(pos.get('long', {}).get('units', 0)) != 0:
                    units = pos['long']['units']
                    side = 'LONG'
                    pnl = pos['long'].get('unrealizedPL', '0')
                elif float(pos.get('short', {}).get('units', 0)) != 0:
                    units = pos['short']['units']
                    side = 'SHORT'
                    pnl = pos['short'].get('unrealizedPL', '0')
                else:
                    continue
                
                pos_msg += f"• {pos['instrument']} {side} {units} units\n"
                pos_msg += f"  💰 P&L: ${float(pnl):.2f}\n\n"
            
            await update.message.reply_text(pos_msg, parse_mode='HTML')
            logger.info("Positions command executed")
        except Exception as e:
            logger.error(f"Error in positions command: {e}")

    async def stop_command(self, update, context):
        """Enhanced /stop command with confirmation"""
        try:
            await update.message.reply_text(
                "🛑 <b>EMERGENCY STOP ACTIVATED</b>\n\n"
                "⚠️ Stopping all trading activities...\n"
                "📊 Generating final report...",
                parse_mode='HTML'
            )
            
            self.running = False
            if self.trader:
                self.trader.stop()
            
            # Send final report
            await self.send_final_report()
            
            logger.info("Enhanced stop command executed")
        except Exception as e:
            logger.error(f"Error in stop command: {e}")

    async def restart_command(self, update, context):
        """New /restart command for restarting trading"""
        try:
            if self.trader:
                await update.message.reply_text(
                    "🔄 <b>RESTARTING TRADING SYSTEM</b>\n\n"
                    "⏳ Reinitializing components...",
                    parse_mode='HTML'
                )
                
                self.trader.stop()
                await asyncio.sleep(2)
                
                # Restart trader
                asyncio.create_task(self.trader.run())
                
                await update.message.reply_text(
                    "✅ <b>TRADING SYSTEM RESTARTED</b>\n\n"
                    "🚀 Bot is back online and trading!",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ Trader not available")
                
            logger.info("Restart command executed")
        except Exception as e:
            logger.error(f"Error in restart command: {e}")

    async def help_command(self, update, context):
        """Enhanced /help command with detailed explanations"""
        try:
            help_text = (
                "🤖 <b>AI Trading Bot v2.0 - Command Guide</b>\n\n"
                "<b>📊 Status & Monitoring:</b>\n"
                "/start - System overview\n"
                "/status - Detailed system status\n"
                "/balance - Account balance & margin\n"
                "/performance - Trading performance metrics\n"
                "/positions - View open positions\n\n"
                "<b>💰 Trading Controls:</b>\n"
                "/profit - P&L summary\n"
                "/risk - Risk management info\n"
                "/stop - Emergency stop all trading\n"
                "/restart - Restart trading system\n\n"
                "<b>ℹ️ Information:</b>\n"
                "/help - This help message\n\n"
                "<b>🚀 Features:</b>\n"
                "• Real-time market analysis\n"
                "• AI-powered trading decisions\n"
                "• Advanced risk management\n"
                "• News sentiment analysis\n"
                "• Performance tracking\n"
                "• Automated reporting"
            )
            
            await update.message.reply_text(help_text, parse_mode='HTML')
            logger.info("Enhanced help command executed")
        except Exception as e:
            logger.error(f"Error in help command: {e}")

    async def handle_message(self, update, context):
        """Enhanced message handler with AI responses"""
        try:
            message_text = update.message.text.lower()
            self.message_count += 1
            
            # AI-like responses based on keywords
            if any(word in message_text for word in ['profit', 'money', 'earnings']):
                response = f"💰 Current total P&L: ${self.performance['total_pnl']:.2f}"
            elif any(word in message_text for word in ['status', 'running', 'working']):
                response = f"🟢 Bot is {'running' if self.running else 'stopped'} - {self.performance['total_trades']} trades executed"
            elif any(word in message_text for word in ['help', 'commands']):
                response = "📋 Use /help to see all available commands"
            else:
                response = "🤖 I'm analyzing markets 24/7. Use /help for commands or /status for updates!"
            
            await update.message.reply_text(response)
            logger.info(f"Enhanced message handled: {message_text[:50]}...")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def error_handler(self, update, context):
        """Enhanced error handler with detailed logging"""
        logger.error(f"Update {update} caused error: {context.error}")
        
        try:
            if isinstance(context.error, RetryAfter):
                logger.warning(f"Rate limited. Waiting {context.error.retry_after} seconds")
                await asyncio.sleep(context.error.retry_after)
            elif isinstance(context.error, NetworkError):
                logger.error("Network error - attempting reconnection")
                await asyncio.sleep(5)
            else:
                logger.error(f"Unexpected error: {context.error}")
                
            # Send error alert
            await self.send_error_alert(str(context.error))
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    async def send_message(self, text: str, parse_mode: str = 'HTML'):
        """Enhanced message sending with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode
                )
                return True
            except TelegramError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error(f"Failed to send message after {max_retries} attempts: {e}")
                return False

    async def send_trade_alert(self, trade_data: Dict[str, Any]):
        """Send real-time trade alerts"""
        try:
            instrument = trade_data.get('instrument', 'Unknown')
            side = trade_data.get('side', 'Unknown')
            units = trade_data.get('units', 0)
            pnl = trade_data.get('pnl', 0)
            
            alert_msg = (
                f"⚡ <b>TRADE EXECUTED</b>\n\n"
                f"📊 <b>Instrument:</b> {instrument}\n"
                f"🎯 <b>Side:</b> {side}\n"
                f"📈 <b>Units:</b> {units}\n"
                f"💰 <b>P&L:</b> ${pnl:.2f}\n"
                f"🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await self.send_message(alert_msg)
            
            # Update performance
            self.performance['total_trades'] += 1
            self.performance['total_pnl'] += pnl
            self.performance['daily_pnl'] += pnl
            
            if pnl > 0:
                self.performance['winning_trades'] += 1
                if pnl > self.performance['best_trade']:
                    self.performance['best_trade'] = pnl
            elif pnl < self.performance['worst_trade']:
                self.performance['worst_trade'] = pnl
                
        except Exception as e:
            logger.error(f"Error sending trade alert: {e}")

    async def send_daily_report(self):
        """Send comprehensive daily performance report"""
        try:
            balance = await self.trader.get_balance() if self.trader else 0
            win_rate = (self.performance['winning_trades'] / max(self.performance['total_trades'], 1)) * 100
            
            report = (
                "📊 <b>DAILY PERFORMANCE REPORT</b>\n\n"
                f"📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}\n"
                f"💰 <b>Account Balance:</b> ${balance:.2f}\n"
                f"📈 <b>Daily P&L:</b> ${self.performance['daily_pnl']:.2f}\n"
                f"🎯 <b>Trades Today:</b> {self.performance['total_trades']}\n"
                f"🏆 <b>Win Rate:</b> {win_rate:.1f}%\n"
                f"🚀 <b>Best Trade:</b> ${self.performance['best_trade']:.2f}\n"
                f"⚠️ <b>Worst Trade:</b> ${self.performance['worst_trade']:.2f}\n\n"
                f"🤖 <b>Status:</b> {'🟢 Active' if self.running else '🔴 Stopped'}\n"
                f"⏰ <b>Uptime:</b> {str(datetime.now() - self.start_time).split('.')[0]}"
            )
            
            await self.send_message(report)
            
            # Reset daily metrics
            self.performance['daily_pnl'] = 0.0
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")

    async def send_error_alert(self, error_msg: str):
        """Send error alerts to user"""
        try:
            alert = (
                f"🚨 <b>SYSTEM ALERT</b>\n\n"
                f"❌ <b>Error:</b> {error_msg[:100]}...\n"
                f"🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n"
                f"🔄 <b>Status:</b> Attempting recovery..."
            )
            await self.send_message(alert)
        except Exception as e:
            logger.error(f"Error sending error alert: {e}")

    async def send_final_report(self):
        """Send final report when stopping"""
        try:
            uptime = datetime.now() - self.start_time
            
            report = (
                "🛑 <b>FINAL SESSION REPORT</b>\n\n"
                f"⏱️ <b>Session Duration:</b> {str(uptime).split('.')[0]}\n"
                f"📊 <b>Total Trades:</b> {self.performance['total_trades']}\n"
                f"💰 <b>Total P&L:</b> ${self.performance['total_pnl']:.2f}\n"
                f"🏆 <b>Win Rate:</b> {(self.performance['winning_trades']/max(self.performance['total_trades'],1)*100):.1f}%\n"
                f"🚀 <b>Best Trade:</b> ${self.performance['best_trade']:.2f}\n"
                f"⚠️ <b>Worst Trade:</b> ${self.performance['worst_trade']:.2f}\n\n"
                f"🤖 <b>Bot Status:</b> Stopped\n"
                f"📅 <b>Shutdown Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            await self.send_message(report)
        except Exception as e:
            logger.error(f"Error sending final report: {e}")

    async def run(self):
        """Enhanced run method with better error handling"""
        try:
            self.running = True
            logger.info("Starting Enhanced Telegram bot...")
            
            # Build application
            self.app = ApplicationBuilder().token(self.token).build()
            
            # Add enhanced handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("balance", self.balance_command))
            self.app.add_handler(CommandHandler("performance", self.performance_command))
            self.app.add_handler(CommandHandler("positions", self.positions_command))
            self.app.add_handler(CommandHandler("stop", self.stop_command))
            self.app.add_handler(CommandHandler("restart", self.restart_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            self.app.add_error_handler(self.error_handler)
            
            logger.info("Enhanced bot handlers registered")
            
            # Send startup message
            await self.send_message(
                "🚀 <b>AI Trading Bot v2.0 ONLINE</b>\n\n"
                "✅ All systems operational\n"
                "🎯 Ready for maximum profit generation\n"
                "📊 Enhanced features activated"
            )
            
            # Schedule daily reports
            asyncio.create_task(self.daily_report_scheduler())
            
            # Run polling with enhanced error handling
            await self.app.run_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query']
            )
            
        except Exception as e:
            logger.error(f"Critical error running enhanced bot: {e}")
            self.running = False
            raise

    async def daily_report_scheduler(self):
        """Schedule daily reports"""
        while self.running:
            try:
                now = datetime.now()
                # Send daily report at 00:00
                if now.hour == 0 and now.minute == 0:
                    await self.send_daily_report()
                    await asyncio.sleep(60)  # Wait 1 minute to avoid duplicate reports
                else:
                    await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in daily report scheduler: {e}")
                await asyncio.sleep(60)

    def stop(self):
        """Enhanced stop method"""
        self.running = False
        if self.app:
            self.app.stop()
        logger.info("Enhanced bot stopped")

# Export for backward compatibility
TradingBot = EnhancedTradingBot