#!/usr/bin/env python3
"""
Report Sender for AI Trading Bot
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

import telegram
from telegram.error import TelegramError, NetworkError, RetryAfter

logger = logging.getLogger(__name__)

class ReportSender:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        
        self.bot = telegram.Bot(token=self.bot_token)
        logger.info("Report sender initialized")

    async def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to the configured chat"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info("Message sent successfully")
            return True
            
        except RetryAfter as e:
            logger.warning(f"Rate limited. Waiting {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
            return await self.send_message(text, parse_mode)
            
        except NetworkError as e:
            logger.error(f"Network error sending message: {e}")
            return False
            
        except TelegramError as e:
            logger.error(f"Telegram error sending message: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    async def send_trading_report(self, report_data: Dict[str, Any]) -> bool:
        """Send a formatted trading report"""
        try:
            report_text = self._format_trading_report(report_data)
            return await self.send_message(report_text)
            
        except Exception as e:
            logger.error(f"Error sending trading report: {e}")
            return False

    def _format_trading_report(self, data: Dict[str, Any]) -> str:
        """Format trading data into a readable report"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            report = f"📊 <b>Trading Report</b>\n"
            report += f"🕒 <i>{timestamp}</i>\n\n"
            
            # Balance information
            if 'balance' in data:
                report += f"💰 <b>Balance:</b> ${data['balance']:.2f}\n"
            
            # Trade count
            if 'trade_count' in data:
                report += f"📈 <b>Trades Today:</b> {data['trade_count']}\n"
            
            # Profit/Loss
            if 'pnl' in data:
                pnl = data['pnl']
                pnl_emoji = "📈" if pnl >= 0 else "📉"
                report += f"{pnl_emoji} <b>P&L:</b> ${pnl:.2f}\n"
            
            # Market sentiment
            if 'sentiment' in data:
                sentiment = data['sentiment']
                sentiment_text = self._get_sentiment_text(sentiment)
                report += f"🎯 <b>Market Sentiment:</b> {sentiment_text}\n"
            
            # Active positions
            if 'positions' in data and data['positions']:
                report += f"\n<b>Active Positions:</b>\n"
                for pos in data['positions']:
                    report += f"• {pos.get('instrument', 'Unknown')} - {pos.get('side', 'Unknown')} - {pos.get('units', 0)} units\n"
            
            # Recent trades
            if 'recent_trades' in data and data['recent_trades']:
                report += f"\n<b>Recent Trades:</b>\n"
                for trade in data['recent_trades'][:5]:  # Show last 5 trades
                    report += f"• {trade.get('instrument', 'Unknown')} {trade.get('side', 'Unknown')} - P&L: ${trade.get('pnl', 0):.2f}\n"
            
            # News headlines
            if 'headlines' in data and data['headlines']:
                report += f"\n<b>Latest News:</b>\n"
                for headline in data['headlines'][:3]:  # Show top 3 headlines
                    report += f"• {headline}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error formatting report: {e}")
            return f"📊 Trading Report\n⚠️ Error formatting report: {str(e)}"

    def _get_sentiment_text(self, sentiment: float) -> str:
        """Convert sentiment score to text"""
        if sentiment >= 0.7:
            return "🟢 Very Bullish"
        elif sentiment >= 0.6:
            return "🟢 Bullish"
        elif sentiment >= 0.4:
            return "🟡 Neutral"
        elif sentiment >= 0.3:
            return "🔴 Bearish"
        else:
            return "🔴 Very Bearish"

    async def send_alert(self, message: str, alert_type: str = "INFO") -> bool:
        """Send an alert message"""
        try:
            emoji_map = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "SUCCESS": "✅"
            }
            
            emoji = emoji_map.get(alert_type, "ℹ️")
            formatted_message = f"{emoji} <b>{alert_type}</b>\n{message}"
            
            return await self.send_message(formatted_message)
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False

    async def send_startup_message(self) -> bool:
        """Send bot startup notification"""
        message = (
            "🚀 <b>AI Trading Bot Started</b>\n\n"
            f"📅 <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
            "🤖 Bot is now active and monitoring markets\n"
            "📊 Reports will be sent automatically"
        )
        return await self.send_message(message)

    async def send_shutdown_message(self) -> bool:
        """Send bot shutdown notification"""
        message = (
            "🛑 <b>AI Trading Bot Stopped</b>\n\n"
            f"📅 <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
            "🤖 Bot has been shut down\n"
            "📊 Final reports have been generated"
        )
        return await self.send_message(message)

# Legacy functions for backward compatibility
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    
    def send_message(text: str):
        """Legacy synchronous function"""
        try:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
            logger.info("Legacy message sent")
        except Exception as e:
            logger.error(f"Legacy message error: {e}")
else:
    def send_message(text: str):
        """Legacy function - no-op if credentials missing"""
        logger.warning("Legacy send_message called but credentials not available")