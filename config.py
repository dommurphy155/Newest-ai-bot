#!/usr/bin/env python3
"""
Configuration Management for AI Trading Bot
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

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
    """API configuration"""
    oanda_api_key: str
    oanda_account_id: str
    telegram_bot_token: str
    telegram_chat_id: str
    hf_token: Optional[str] = None
    oanda_environment: str = "practice"  # or "live"

    def __post_init__(self):
        if not all([self.oanda_api_key, self.oanda_account_id, 
                   self.telegram_bot_token, self.telegram_chat_id]):
            raise ValueError("Missing required API credentials")

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "data/trading_bot.db"
    backup_interval: int = 3600  # 1 hour
    max_backups: int = 24

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_file: str = "logs/bot.log"
    error_file: str = "logs/error.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

class Config:
    """Main configuration class"""
    def __init__(self):
        self.trading = TradingConfig()
        self.api = APIConfig(
            oanda_api_key=os.getenv('OANDA_API_KEY', ''),
            oanda_account_id=os.getenv('OANDA_ACCOUNT_ID', ''),
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID', ''),
            hf_token=os.getenv('HF_TOKEN'),
            oanda_environment=os.getenv('OANDA_ENVIRONMENT', 'practice')
        )
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