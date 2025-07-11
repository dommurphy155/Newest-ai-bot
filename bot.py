#!/usr/bin/env python3
"""
🚀 ULTRA-OPTIMIZED TELEGRAM BOT v3.0
Production-ready with advanced monitoring and alerts
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import psutil
import gc

try:
    import telegram
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    from telegram.error import TelegramError, NetworkError, RetryAfter
except ImportError as e:
    logging.error(f"Telegram imports failed: {e}")
    raise

logger = logging.getLogger(__name__)

class UltraOptimizedTradingBot:
    def __init__(self, token: str, chat_id: str, trader=None, database=None):
        self.token = token
        self.chat_id = chat_id
        self.trader = trader
        self.database = database
        self.app = None
        self.running = False
        self.start_time = datetime.now()
        self.message_count = 0
        self.last_heartbeat = datetime.now()
        
        # Enhanced performance tracking
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'daily_pnl': 0.0,
            'hourly_pnl': 0.0,
            'peak_balance': 0.0,
            'current_balance': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'sharpe_ratio': 0.0
        }
        
        # Strategy performance tracking
        self.strategy_performance = {
            'momentum_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'mean_reversion': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'breakout_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'sentiment_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'volatility_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'correlation_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'news_trading': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'ml_prediction': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'arbitrage': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0},
            'scalping': {'wins': 0, 'losses': 0, 'pnl': 0.0, 'win_rate': 0.0}
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'profit_alert': 100.0,  # Alert every $100 profit
            'loss_alert': -50.0,    # Alert every $50 loss
            'drawdown_alert': 0.05, # Alert at 5% drawdown
            'win_rate_alert': 0.6,  # Alert if win rate drops below 60%
            'memory_alert': 80.0,   # Alert if memory usage > 80%
            'cpu_alert': 80.0       # Alert if CPU usage > 80%
        }
        
        # System monitoring
        self.system_metrics = {
            'memory_usage': 0.0,
            'cpu_usage': 0.0,
            'uptime': 0.0,
            'message_rate': 0.0
        }
        
        try:
            self.bot = telegram.Bot(token=self.token)
            logger.info("🚀 Ultra-Optimized Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram bot: {e}")
            raise

    async def start_command(self, update, context):
        """Enhanced /start command with comprehensive system info"""
        try:
            uptime = datetime.now() - self.start_time
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            status_msg = (
                "🚀 <b>ULTRA-OPTIMIZED AI Trading Bot v3.0</b>\n\n"
                f"⏰ <b>Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"📊 <b>Status:</b> {'🟢 Running' if self.running else '🔴 Stopped'}\n"
                f"💼 <b>Trader:</b> {'🟢 Active' if self.trader and self.trader.running else '🔴 Inactive'}\n"
                f"💾 <b>Memory:</b> {memory.percent:.1f}%\n"
                f"🖥️ <b>CPU:</b> {cpu_percent:.1f}%\n"
                f"💬 <b>Messages:</b> {self.message_count}\n\n"
                "<b>📈 Performance Summary:</b>\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}\n"
                f"• Peak Balance: ${self.performance['peak_balance']:.2f}\n\n"
                "<b>🎯 Available Commands:</b>\n"
                "/start - System status\n"
                "/status - Detailed status\n"
                "/balance - Account balance\n"
                "/performance - Trading performance\n"
                "/strategies - Strategy performance\n"
                "/positions - Open positions\n"
                "/profit - P&L summary\n"
                "/risk - Risk management\n"
                "/system - System metrics\n"
                "/stop - Emergency stop\n"
                "/restart - Restart trading\n"
                "/help - Command help"
            )
            
            await update.message.reply_text(status_msg, parse_mode='HTML')
            self.message_count += 1
            logger.info("✅ Enhanced start command executed")
        except Exception as e:
            logger.error(f"❌ Error in start command: {e}")

    async def status_command(self, update, context):
        """Enhanced /status command with detailed metrics"""
        try:
            uptime = datetime.now() - self.start_time
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get trader status
            trader_status = {}
            if self.trader:
                trader_status = await self.trader.get_detailed_status()
            
            status_msg = (
                "📊 <b>DETAILED SYSTEM STATUS REPORT</b>\n\n"
                f"🕒 <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏱️ <b>Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"🤖 <b>Bot Status:</b> {'🟢 Active' if self.running else '🔴 Inactive'}\n"
                f"📈 <b>Trader Status:</b> {'🟢 Trading' if trader_status.get('running') else '🔴 Stopped'}\n"
                f"💬 <b>Messages:</b> {self.message_count}\n"
                f"🔄 <b>Heartbeat:</b> {(datetime.now() - self.last_heartbeat).seconds}s ago\n\n"
                f"💾 <b>System Resources:</b>\n"
                f"• Memory Usage: {memory.percent:.1f}%\n"
                f"• CPU Usage: {cpu_percent:.1f}%\n"
                f"• Available Memory: {memory.available / 1024 / 1024:.1f}MB\n\n"
                f"📊 <b>Trading Performance:</b>\n"
                f"• Total Trades: {self.performance['total_trades']}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}\n"
                f"• Peak Balance: ${self.performance['peak_balance']:.2f}\n"
                f"• Max Drawdown: {self.performance['max_drawdown']:.2f}%\n"
                f"• Profit Factor: {self.performance['profit_factor']:.2f}\n"
                f"• Sharpe Ratio: {self.performance['sharpe_ratio']:.2f}"
            )
            
            await update.message.reply_text(status_msg, parse_mode='HTML')
            self.last_heartbeat = datetime.now()
            logger.info("✅ Enhanced status command executed")
        except Exception as e:
            logger.error(f"❌ Error in status command: {e}")

    async def balance_command(self, update, context):
        """Enhanced /balance command with account details"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            balance = await self.trader.get_balance()
            
            if balance is None:
                await update.message.reply_text("❌ Failed to retrieve balance")
                return
            
            # Calculate additional metrics
            balance_change = balance - self.performance['current_balance'] if self.performance['current_balance'] > 0 else 0
            balance_change_pct = (balance_change / self.performance['current_balance'] * 100) if self.performance['current_balance'] > 0 else 0
            
            # Update peak balance
            if balance > self.performance['peak_balance']:
                self.performance['peak_balance'] = balance
            
            # Calculate drawdown
            if self.performance['peak_balance'] > 0:
                drawdown = (self.performance['peak_balance'] - balance) / self.performance['peak_balance'] * 100
                self.performance['max_drawdown'] = max(self.performance['max_drawdown'], drawdown)
            
            self.performance['current_balance'] = balance
            
            balance_msg = (
                "💰 <b>ACCOUNT BALANCE DETAILS</b>\n\n"
                f"💵 <b>Current Balance:</b> ${balance:.2f}\n"
                f"📈 <b>Peak Balance:</b> ${self.performance['peak_balance']:.2f}\n"
                f"📊 <b>Balance Change:</b> ${balance_change:.2f} ({balance_change_pct:+.2f}%)\n"
                f"📉 <b>Max Drawdown:</b> {self.performance['max_drawdown']:.2f}%\n\n"
                f"📊 <b>Performance Metrics:</b>\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}\n"
                f"• Best Trade: ${self.performance['best_trade']:.2f}\n"
                f"• Worst Trade: ${self.performance['worst_trade']:.2f}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Profit Factor: {self.performance['profit_factor']:.2f}"
            )
            
            await update.message.reply_text(balance_msg, parse_mode='HTML')
            logger.info("✅ Enhanced balance command executed")
        except Exception as e:
            logger.error(f"❌ Error in balance command: {e}")

    async def performance_command(self, update, context):
        """Enhanced /performance command for detailed metrics"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            # Calculate advanced metrics
            total_trades = self.performance['total_trades']
            winning_trades = self.performance['winning_trades']
            total_pnl = self.performance['total_pnl']
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            avg_trade = total_pnl / total_trades if total_trades > 0 else 0
            profit_factor = self.performance['profit_factor']
            sharpe_ratio = self.performance['sharpe_ratio']
            
            perf_msg = (
                "🎯 <b>DETAILED TRADING PERFORMANCE</b>\n\n"
                f"📈 <b>Trade Statistics:</b>\n"
                f"• Total Trades: {total_trades}\n"
                f"• Winning Trades: {winning_trades}\n"
                f"• Losing Trades: {total_trades - winning_trades}\n"
                f"• Win Rate: {win_rate:.1f}%\n\n"
                f"💰 <b>Profitability Metrics:</b>\n"
                f"• Total P&L: ${total_pnl:.2f}\n"
                f"• Average Trade: ${avg_trade:.2f}\n"
                f"• Best Trade: ${self.performance['best_trade']:.2f}\n"
                f"• Worst Trade: ${self.performance['worst_trade']:.2f}\n"
                f"• Daily P&L: ${self.performance['daily_pnl']:.2f}\n"
                f"• Hourly P&L: ${self.performance['hourly_pnl']:.2f}\n\n"
                f"📊 <b>Risk Metrics:</b>\n"
                f"• Profit Factor: {profit_factor:.2f}\n"
                f"• Sharpe Ratio: {sharpe_ratio:.2f}\n"
                f"• Max Drawdown: {self.performance['max_drawdown']:.2f}%\n"
                f"• Peak Balance: ${self.performance['peak_balance']:.2f}"
            )
            
            await update.message.reply_text(perf_msg, parse_mode='HTML')
            logger.info("✅ Performance command executed")
        except Exception as e:
            logger.error(f"❌ Error in performance command: {e}")

    async def strategies_command(self, update, context):
        """New /strategies command for strategy performance"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            # Get strategy performance from trader
            trader_status = await self.trader.get_detailed_status()
            strategy_performance = trader_status.get('strategy_performance', {})
            
            if not strategy_performance:
                await update.message.reply_text("📊 No strategy performance data available")
                return
            
            strategy_msg = "📊 <b>STRATEGY PERFORMANCE ANALYSIS</b>\n\n"
            
            # Sort strategies by win rate
            sorted_strategies = sorted(
                strategy_performance.items(),
                key=lambda x: x[1].get('win_rate', 0),
                reverse=True
            )
            
            for strategy, perf in sorted_strategies[:10]:  # Top 10 strategies
                wins = perf.get('wins', 0)
                losses = perf.get('losses', 0)
                pnl = perf.get('pnl', 0.0)
                total_trades = wins + losses
                win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
                
                strategy_msg += f"🎯 <b>{strategy.replace('_', ' ').title()}</b>\n"
                strategy_msg += f"• Trades: {total_trades} | Wins: {wins} | Losses: {losses}\n"
                strategy_msg += f"• Win Rate: {win_rate:.1f}% | P&L: ${pnl:.2f}\n\n"
            
            await update.message.reply_text(strategy_msg, parse_mode='HTML')
            logger.info("✅ Strategies command executed")
        except Exception as e:
            logger.error(f"❌ Error in strategies command: {e}")

    async def system_command(self, update, context):
        """New /system command for system metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            uptime = datetime.now() - self.start_time
            
            system_msg = (
                "🖥️ <b>SYSTEM METRICS & MONITORING</b>\n\n"
                f"⏰ <b>System Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"💾 <b>Memory Usage:</b> {memory.percent:.1f}% ({memory.used / 1024 / 1024:.1f}MB / {memory.total / 1024 / 1024:.1f}MB)\n"
                f"🖥️ <b>CPU Usage:</b> {cpu_percent:.1f}%\n"
                f"💿 <b>Disk Usage:</b> {disk.percent:.1f}% ({disk.used / 1024 / 1024 / 1024:.1f}GB / {disk.total / 1024 / 1024 / 1024:.1f}GB)\n\n"
                f"📊 <b>Bot Metrics:</b>\n"
                f"• Messages Sent: {self.message_count}\n"
                f"• Message Rate: {self.system_metrics['message_rate']:.1f} msg/min\n"
                f"• Last Heartbeat: {(datetime.now() - self.last_heartbeat).seconds}s ago\n\n"
                f"⚠️ <b>Alert Thresholds:</b>\n"
                f"• Memory Alert: >{self.alert_thresholds['memory_alert']:.0f}%\n"
                f"• CPU Alert: >{self.alert_thresholds['cpu_alert']:.0f}%\n"
                f"• Profit Alert: >${self.alert_thresholds['profit_alert']:.0f}\n"
                f"• Loss Alert: <${self.alert_thresholds['loss_alert']:.0f}"
            )
            
            await update.message.reply_text(system_msg, parse_mode='HTML')
            logger.info("✅ System command executed")
        except Exception as e:
            logger.error(f"❌ Error in system command: {e}")

    async def stop_command(self, update, context):
        """Enhanced /stop command with confirmation"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            # Emergency stop
            self.trader.stop()
            
            stop_msg = (
                "🛑 <b>EMERGENCY STOP EXECUTED</b>\n\n"
                f"⏰ <b>Stopped at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📊 <b>Final Performance:</b>\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Total Trades: {self.performance['total_trades']}\n\n"
                f"⚠️ <b>All trading operations stopped</b>\n"
                f"Use /restart to resume trading"
            )
            
            await update.message.reply_text(stop_msg, parse_mode='HTML')
            logger.warning("🛑 Emergency stop executed")
        except Exception as e:
            logger.error(f"❌ Error in stop command: {e}")

    async def restart_command(self, update, context):
        """Enhanced /restart command"""
        try:
            if not self.trader:
                await update.message.reply_text("❌ Trader not initialized")
                return
            
            # Restart trader
            self.trader.running = True
            asyncio.create_task(self.trader.run())
            
            restart_msg = (
                "🔄 <b>TRADING RESTARTED</b>\n\n"
                f"⏰ <b>Restarted at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"📊 <b>Previous Performance:</b>\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Total Trades: {self.performance['total_trades']}\n\n"
                f"✅ <b>Trading operations resumed</b>"
            )
            
            await update.message.reply_text(restart_msg, parse_mode='HTML')
            logger.info("🔄 Trading restarted")
        except Exception as e:
            logger.error(f"❌ Error in restart command: {e}")

    async def help_command(self, update, context):
        """Enhanced /help command with detailed descriptions"""
        try:
            help_msg = (
                "📚 <b>ULTRA-OPTIMIZED TRADING BOT COMMANDS</b>\n\n"
                "<b>📊 Status Commands:</b>\n"
                "/start - System overview and quick status\n"
                "/status - Detailed system status with metrics\n"
                "/balance - Account balance and performance\n"
                "/performance - Comprehensive trading performance\n"
                "/strategies - Strategy performance analysis\n"
                "/system - System resources and monitoring\n\n"
                "<b>🎯 Trading Commands:</b>\n"
                "/positions - View open positions\n"
                "/profit - P&L summary and analysis\n"
                "/risk - Risk management settings\n\n"
                "<b>⚙️ Control Commands:</b>\n"
                "/stop - Emergency stop all trading\n"
                "/restart - Restart trading operations\n"
                "/help - Show this help message\n\n"
                "<b>📈 Features:</b>\n"
                "• 30+ Profit-Maximizing Strategies\n"
                "• Advanced Risk Management\n"
                "• Real-time Performance Monitoring\n"
                "• System Resource Optimization\n"
                "• Automatic Alert System\n"
                "• Strategy Performance Tracking"
            )
            
            await update.message.reply_text(help_msg, parse_mode='HTML')
            logger.info("✅ Help command executed")
        except Exception as e:
            logger.error(f"❌ Error in help command: {e}")

    async def handle_message(self, update, context):
        """Handle general messages"""
        try:
            message = update.message.text.lower()
            
            if 'profit' in message or 'pnl' in message:
                await self.performance_command(update, context)
            elif 'balance' in message:
                await self.balance_command(update, context)
            elif 'status' in message:
                await self.status_command(update, context)
            elif 'help' in message:
                await self.help_command(update, context)
            else:
                await update.message.reply_text(
                    "🤖 I'm an AI trading bot. Use /help to see available commands."
                )
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")

    async def error_handler(self, update, context):
        """Enhanced error handler"""
        try:
            logger.error(f"Telegram error: {context.error}")
            
            if isinstance(context.error, RetryAfter):
                await asyncio.sleep(context.error.retry_after)
            elif isinstance(context.error, NetworkError):
                await asyncio.sleep(5)
            
            # Send error alert
            await self.send_error_alert(f"Telegram error: {context.error}")
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    async def send_message(self, text: str, parse_mode: str = 'HTML'):
        """Send message with retry logic"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            self.message_count += 1
            return True
        except TelegramError as e:
            logger.error(f"Telegram error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def send_trade_alert(self, trade_data: Dict[str, Any]):
        """Send enhanced trade alert"""
        try:
            instrument = trade_data.get('instrument', 'Unknown')
            side = trade_data.get('side', 'Unknown')
            units = trade_data.get('units', 0)
            price = trade_data.get('price', 0.0)
            strategy = trade_data.get('strategy', 'Unknown')
            confidence = trade_data.get('analysis', {}).get('confidence', 0.0)
            
            alert_msg = (
                f"🎯 <b>TRADE EXECUTED</b>\n\n"
                f"📊 <b>Instrument:</b> {instrument}\n"
                f"📈 <b>Side:</b> {side}\n"
                f"📊 <b>Units:</b> {units:,}\n"
                f"💰 <b>Price:</b> {price:.5f}\n"
                f"🎯 <b>Strategy:</b> {strategy.replace('_', ' ').title()}\n"
                f"📊 <b>Confidence:</b> {confidence:.1%}\n"
                f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await self.send_message(alert_msg)
            logger.info(f"✅ Trade alert sent: {instrument} {side} {units}")
        except Exception as e:
            logger.error(f"❌ Error sending trade alert: {e}")

    async def send_daily_report(self):
        """Send comprehensive daily report"""
        try:
            if not self.trader:
                return
            
            # Get trader status
            trader_status = await self.trader.get_detailed_status()
            
            # Calculate daily metrics
            today = datetime.now().date()
            daily_trades = [t for t in self.trader.trade_history if t['timestamp'].date() == today]
            daily_pnl = sum(t.get('pnl', 0) for t in daily_trades)
            daily_trade_count = len(daily_trades)
            
            # Update performance
            self.performance['daily_pnl'] = daily_pnl
            self.performance['total_trades'] = trader_status.get('trade_count', 0)
            self.performance['winning_trades'] = trader_status.get('profitable_trades', 0)
            self.performance['total_pnl'] = trader_status.get('total_pnl', 0.0)
            
            # Calculate win rate
            if self.performance['total_trades'] > 0:
                self.performance['win_rate'] = (self.performance['winning_trades'] / self.performance['total_trades']) * 100
            
            report_msg = (
                f"📊 <b>DAILY TRADING REPORT</b>\n"
                f"📅 {today.strftime('%Y-%m-%d')}\n\n"
                f"📈 <b>Daily Performance:</b>\n"
                f"• Trades: {daily_trade_count}\n"
                f"• P&L: ${daily_pnl:.2f}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n\n"
                f"📊 <b>Overall Performance:</b>\n"
                f"• Total Trades: {self.performance['total_trades']}\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Peak Balance: ${self.performance['peak_balance']:.2f}\n"
                f"• Max Drawdown: {self.performance['max_drawdown']:.2f}%\n\n"
                f"🖥️ <b>System Status:</b>\n"
                f"• Uptime: {str(datetime.now() - self.start_time).split('.')[0]}\n"
                f"• Memory: {psutil.virtual_memory().percent:.1f}%\n"
                f"• CPU: {psutil.cpu_percent(interval=1):.1f}%"
            )
            
            await self.send_message(report_msg)
            logger.info("✅ Daily report sent")
        except Exception as e:
            logger.error(f"❌ Error sending daily report: {e}")

    async def send_error_alert(self, error_msg: str):
        """Send error alert"""
        try:
            alert_msg = (
                f"⚠️ <b>SYSTEM ALERT</b>\n\n"
                f"❌ <b>Error:</b> {error_msg}\n"
                f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🖥️ <b>System:</b> {psutil.virtual_memory().percent:.1f}% memory, {psutil.cpu_percent(interval=1):.1f}% CPU"
            )
            
            await self.send_message(alert_msg)
            logger.error(f"⚠️ Error alert sent: {error_msg}")
        except Exception as e:
            logger.error(f"❌ Error sending error alert: {e}")

    async def send_final_report(self):
        """Send final performance report"""
        try:
            uptime = datetime.now() - self.start_time
            
            final_msg = (
                f"📊 <b>FINAL PERFORMANCE REPORT</b>\n\n"
                f"⏰ <b>Total Uptime:</b> {str(uptime).split('.')[0]}\n"
                f"📈 <b>Final Performance:</b>\n"
                f"• Total Trades: {self.performance['total_trades']}\n"
                f"• Win Rate: {self.performance['win_rate']:.1f}%\n"
                f"• Total P&L: ${self.performance['total_pnl']:.2f}\n"
                f"• Peak Balance: ${self.performance['peak_balance']:.2f}\n"
                f"• Max Drawdown: {self.performance['max_drawdown']:.2f}%\n"
                f"• Profit Factor: {self.performance['profit_factor']:.2f}\n"
                f"• Sharpe Ratio: {self.performance['sharpe_ratio']:.2f}\n\n"
                f"💬 <b>Messages Sent:</b> {self.message_count}\n"
                f"🛑 <b>Bot Shutdown Complete</b>"
            )
            
            await self.send_message(final_msg)
            logger.info("📊 Final report sent")
        except Exception as e:
            logger.error(f"❌ Error sending final report: {e}")

    async def run(self):
        """Main run method with enhanced features"""
        try:
            self.running = True
            
            # Build application
            self.app = ApplicationBuilder().token(self.token).build()
            
            # Add command handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("balance", self.balance_command))
            self.app.add_handler(CommandHandler("performance", self.performance_command))
            self.app.add_handler(CommandHandler("strategies", self.strategies_command))
            self.app.add_handler(CommandHandler("system", self.system_command))
            self.app.add_handler(CommandHandler("stop", self.stop_command))
            self.app.add_handler(CommandHandler("restart", self.restart_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            
            # Add message handler
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            self.app.add_error_handler(self.error_handler)
            
            # Start the bot
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            logger.info("🚀 Ultra-Optimized Telegram Bot started")
            
            # Start background tasks
            await asyncio.gather(
                self.daily_report_scheduler(),
                self.system_monitor()
            )
            
        except Exception as e:
            logger.error(f"❌ Error in bot run: {e}")
        finally:
            self.running = False

    async def daily_report_scheduler(self):
        """Schedule daily reports"""
        while self.running:
            try:
                now = datetime.now()
                next_report = now.replace(hour=18, minute=0, second=0, microsecond=0)
                
                if now.hour >= 18:
                    next_report += timedelta(days=1)
                
                wait_seconds = (next_report - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                if self.running:
                    await self.send_daily_report()
                    
            except Exception as e:
                logger.error(f"❌ Error in daily report scheduler: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def system_monitor(self):
        """Monitor system resources"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Update system metrics
                self.system_metrics['memory_usage'] = memory.percent
                self.system_metrics['cpu_usage'] = cpu_percent
                self.system_metrics['uptime'] = (datetime.now() - self.start_time).total_seconds()
                
                # Send alerts if thresholds exceeded
                if memory.percent > self.alert_thresholds['memory_alert']:
                    await self.send_error_alert(f"High memory usage: {memory.percent:.1f}%")
                
                if cpu_percent > self.alert_thresholds['cpu_alert']:
                    await self.send_error_alert(f"High CPU usage: {cpu_percent:.1f}%")
                    
            except Exception as e:
                logger.error(f"❌ Error in system monitor: {e}")

    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.app:
            asyncio.create_task(self.app.stop())
        logger.info("🛑 Ultra-Optimized Telegram Bot stopped")