#!/usr/bin/env python3
"""
Configuration Management for AI Trading Bot
Direct configuration without .env files for Ubuntu 20.04 compatibility
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    max_spread: float = 0.0003
    risk_per_trade: float = 0.015  # 1.5% risk per trade
    max_position_size: int = 50000
    min_confidence: float = 0.75
    stop_loss_pips: int = 20
    take_profit_pips: int = 40
    max_daily_trades: int = 50
    max_open_positions: int = 5
    instruments: List[str] = None

    def __post_init__(self):
        if self.instruments is None:
            self.instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CAD', 'AUD_USD', 'EUR_GBP']

@dataclass
class APIConfig:
    """API configuration - CONFIGURE YOUR CREDENTIALS HERE"""
    # CONFIGURE THESE VALUES DIRECTLY:
    oanda_api_key: str = "your_oanda_api_key_here"
    oanda_account_id: str = "your_oanda_account_id_here"
    telegram_bot_token: str = "your_telegram_bot_token_here"
    telegram_chat_id: str = "your_telegram_chat_id_here"
    hf_token: Optional[str] = None  # Optional Hugging Face token
    oanda_environment: str = "practice"  # or "live"

    def __post_init__(self):
        # Check if user has configured credentials
        if (self.oanda_api_key == "your_oanda_api_key_here" or 
            self.oanda_account_id == "your_oanda_account_id_here" or
            self.telegram_bot_token == "your_telegram_bot_token_here" or
            self.telegram_chat_id == "your_telegram_chat_id_here"):
            
            print("🔧 CONFIGURATION REQUIRED:")
            print("Edit config.py and replace the placeholder values with your real API credentials:")
            print("- oanda_api_key: Get from OANDA account")
            print("- oanda_account_id: Your OANDA account ID")
            print("- telegram_bot_token: Create bot with @BotFather on Telegram")
            print("- telegram_chat_id: Your Telegram chat ID")
            print("\nAlternatively, export as environment variables:")
            print("export OANDA_API_KEY='your_key'")
            print("export OANDA_ACCOUNT_ID='your_account'")
            print("export TELEGRAM_BOT_TOKEN='your_token'")
            print("export TELEGRAM_CHAT_ID='your_chat_id'")
            
            # Try environment variables as fallback
            env_key = os.environ.get('OANDA_API_KEY')
            env_account = os.environ.get('OANDA_ACCOUNT_ID')
            env_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            env_chat = os.environ.get('TELEGRAM_CHAT_ID')
            
            if env_key and env_account and env_token and env_chat:
                self.oanda_api_key = env_key
                self.oanda_account_id = env_account
                self.telegram_bot_token = env_token
                self.telegram_chat_id = env_chat
                print("✅ Using environment variables")
            else:
                print("❌ Please configure your API credentials before running the bot")

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "data/trading_bot.db"
    backup_interval: int = 3600  # 1 hour
    max_backups: int = 24
    
    # Memory optimization settings - Using more memory for better performance
    max_memory_mb: int = 512  # Allow up to 512MB for database operations
    cache_size_kb: int = 8192  # 8MB cache (increased from 2MB)

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    error_file: str = "logs/error.log"
    max_file_size: int = 20 * 1024 * 1024  # 20MB (increased from 5MB)
    backup_count: int = 10  # Increased from 3 for better history

class Config:
    """Main configuration class optimized for Ubuntu 20.04 + Python 3.8.10"""
    def __init__(self):
        self.trading = TradingConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self._ensure_paths()
        self._validate()

    def _ensure_paths(self):
        """Ensure required directories exist for logs and database."""
        os.makedirs(os.path.dirname(self.database.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.logging.log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.logging.error_file), exist_ok=True)

    def _validate(self):
        """Validate configuration parameters"""
        errors = []
        if self.trading.risk_per_trade <= 0 or self.trading.risk_per_trade > 0.1:
            errors.append("Risk per trade must be between 0 and 0.1 (10%)")
        if self.trading.max_spread <= 0:
            errors.append("Max spread must be positive")
        if self.trading.min_confidence < 0.5 or self.trading.min_confidence > 1.0:
            errors.append("Min confidence must be between 0.5 and 1.0")
            
        # Only validate credentials if they're not placeholder values
        if (self.api.oanda_api_key != "your_oanda_api_key_here" and
            self.api.oanda_account_id != "your_oanda_account_id_here" and
            self.api.telegram_bot_token != "your_telegram_bot_token_here" and
            self.api.telegram_chat_id != "your_telegram_chat_id_here"):
            
            if not self.api.oanda_api_key:
                errors.append("OANDA_API_KEY is required")
            if not self.api.oanda_account_id:
                errors.append("OANDA_ACCOUNT_ID is required")
            if not self.api.telegram_bot_token:
                errors.append("TELEGRAM_BOT_TOKEN is required")
            if not self.api.telegram_chat_id:
                errors.append("TELEGRAM_CHAT_ID is required")
                
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))

    def get_oanda_url(self) -> str:
        """Get OANDA API URL based on environment"""
        if self.api.oanda_environment == "live":
            return "https://api-fxtrade.oanda.com"
        return "https://api-fxpractice.oanda.com"

    def to_dict(self) -> Dict:
        """Convert config to dictionary (excluding sensitive info)"""
        return {
            'trading': self.trading.__dict__,
            'api': {k: v for k, v in self.api.__dict__.items() 
                   if k not in ['oanda_api_key', 'telegram_bot_token']},
            'database': self.database.__dict__,
            'logging': self.logging.__dict__
        }

# Global configuration instance
config = Config()