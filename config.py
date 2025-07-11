#!/usr/bin/env python3
"""
Configuration Management for AI Trading Bot
Production-ready configuration using environment variables only
Optimized for Ubuntu 20.04 + Python 3.8.10
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
    """API configuration using environment variables"""
    oanda_api_key: str
    oanda_account_id: str
    telegram_bot_token: str
    telegram_chat_id: str
    hf_token: Optional[str] = None
    oanda_environment: str = "practice"

    def __init__(self):
        # Get required environment variables
        self.oanda_api_key = os.environ.get('OANDA_API_KEY', '')
        self.oanda_account_id = os.environ.get('OANDA_ACCOUNT_ID', '')
        self.telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        self.hf_token = os.environ.get('HF_TOKEN')
        self.oanda_environment = os.environ.get('OANDA_ENVIRONMENT', 'practice')
        
        # Validate required credentials
        missing_vars = []
        if not self.oanda_api_key:
            missing_vars.append('OANDA_API_KEY')
        if not self.oanda_account_id:
            missing_vars.append('OANDA_ACCOUNT_ID')
        if not self.telegram_bot_token:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not self.telegram_chat_id:
            missing_vars.append('TELEGRAM_CHAT_ID')
            
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please export these variables before running the bot:\n"
                f"export OANDA_API_KEY='your_api_key'\n"
                f"export OANDA_ACCOUNT_ID='your_account_id'\n"
                f"export TELEGRAM_BOT_TOKEN='your_bot_token'\n"
                f"export TELEGRAM_CHAT_ID='your_chat_id'\n"
                f"export OANDA_ENVIRONMENT='practice'  # or 'live'"
            )

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "data/trading_bot.db"
    backup_interval: int = 3600  # 1 hour
    max_backups: int = 24
    
    # Memory optimization settings
    max_memory_mb: int = 512
    cache_size_kb: int = 8192

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    error_file: str = "logs/error.log"
    max_file_size: int = 20 * 1024 * 1024  # 20MB
    backup_count: int = 10

class Config:
    """Main configuration class for production deployment"""
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