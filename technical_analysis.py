#!/usr/bin/env python3
"""
Advanced Technical Analysis for AI Trading Bot
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TechnicalIndicators:
    """Technical indicators data structure"""
    rsi: float = 50.0
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    bollinger_upper: float = 0.0
    bollinger_lower: float = 0.0
    bollinger_middle: float = 0.0
    sma_20: float = 0.0
    sma_50: float = 0.0
    ema_12: float = 0.0
    ema_26: float = 0.0
    stoch_k: float = 50.0
    stoch_d: float = 50.0
    atr: float = 0.0
    adx: float = 0.0
    williams_r: float = -50.0
    momentum: float = 0.0
    roc: float = 0.0
    cci: float = 0.0

@dataclass
class MarketSignal:
    """Market signal with confidence and reasoning"""
    signal: str  # BUY, SELL, HOLD
    confidence: float
    strength: float
    reasoning: List[str]
    indicators: TechnicalIndicators
    timestamp: datetime

class TechnicalAnalyzer:
    """Advanced technical analysis engine"""
    
    def __init__(self):
        self.price_history: Dict[str, List[Dict]] = {}
        self.max_history_length = 200
    
    def add_price_data(self, instrument: str, price_data: Dict):
        """Add price data to history"""
        if instrument not in self.price_history:
            self.price_history[instrument] = []
        
        self.price_history[instrument].append({
            'timestamp': datetime.now(),
            'bid': price_data.get('bid', 0),
            'ask': price_data.get('ask', 0),
            'mid': (price_data.get('bid', 0) + price_data.get('ask', 0)) / 2,
            'spread': price_data.get('ask', 0) - price_data.get('bid', 0)
        })
        
        # Keep only recent data
        if len(self.price_history[instrument]) > self.max_history_length:
            self.price_history[instrument] = self.price_history[instrument][-self.max_history_length:]
    
    def get_price_dataframe(self, instrument: str) -> Optional[pd.DataFrame]:
        """Convert price history to pandas DataFrame"""
        if instrument not in self.price_history or len(self.price_history[instrument]) < 20:
            return None
        
        df = pd.DataFrame(self.price_history[instrument])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band, sma
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = self.calculate_atr(high, low, close, 1)
        plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / tr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / tr)
        
        dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/period).mean()
        return adx
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams_r
    
    def calculate_momentum(self, prices: pd.Series, period: int = 10) -> pd.Series:
        """Calculate Momentum"""
        return prices.diff(period)
    
    def calculate_roc(self, prices: pd.Series, period: int = 12) -> pd.Series:
        """Calculate Rate of Change"""
        return ((prices / prices.shift(period)) - 1) * 100
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        return cci
    
    def calculate_all_indicators(self, instrument: str) -> Optional[TechnicalIndicators]:
        """Calculate all technical indicators for an instrument"""
        df = self.get_price_dataframe(instrument)
        if df is None or len(df) < 50:
            return None
        
        try:
            # Use mid price for most calculations
            close = df['mid']
            high = df['ask']  # Approximate high with ask
            low = df['bid']   # Approximate low with bid
            
            # Calculate all indicators
            rsi = self.calculate_rsi(close)
            macd, macd_signal, macd_histogram = self.calculate_macd(close)
            bollinger_upper, bollinger_lower, bollinger_middle = self.calculate_bollinger_bands(close)
            sma_20 = close.