#!/usr/bin/env python3
"""
Advanced Technical Analysis for AI Trading Bot
Lightweight replacement for TA-Lib - optimized for Ubuntu 20.04 Python 3.8
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
    obv: float = 0.0  # On Balance Volume
    mfi: float = 50.0  # Money Flow Index
    vwap: float = 0.0  # Volume Weighted Average Price

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
    """Advanced technical analysis engine - lightweight TA-Lib replacement"""
    
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
            'spread': price_data.get('ask', 0) - price_data.get('bid', 0),
            'volume': price_data.get('volume', 1000)  # Default volume for forex
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
    
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On Balance Volume"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Money Flow Index"""
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = pd.Series(index=close.index, dtype=float)
        negative_flow = pd.Series(index=close.index, dtype=float)
        
        for i in range(1, len(typical_price)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
                negative_flow.iloc[i] = 0
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
                positive_flow.iloc[i] = 0
            else:
                positive_flow.iloc[i] = 0
                negative_flow.iloc[i] = 0
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfr = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + mfr))
        
        return mfi
    
    def calculate_vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    def calculate_ichimoku(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, pd.Series]:
        """Calculate Ichimoku Cloud components"""
        # Tenkan Sen (Conversion Line)
        tenkan_sen = (high.rolling(9).max() + low.rolling(9).min()) / 2
        
        # Kijun Sen (Base Line)
        kijun_sen = (high.rolling(26).max() + low.rolling(26).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-26)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    def calculate_fibonacci_retracements(self, high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            'level_0': high,
            'level_236': high - 0.236 * diff,
            'level_382': high - 0.382 * diff,
            'level_500': high - 0.500 * diff,
            'level_618': high - 0.618 * diff,
            'level_786': high - 0.786 * diff,
            'level_100': low
        }
    
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
            volume = df['volume']
            
            # Calculate all indicators
            rsi = self.calculate_rsi(close)
            macd, macd_signal, macd_histogram = self.calculate_macd(close)
            bollinger_upper, bollinger_lower, bollinger_middle = self.calculate_bollinger_bands(close)
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]
            stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
            atr = self.calculate_atr(high, low, close).iloc[-1]
            adx = self.calculate_adx(high, low, close).iloc[-1]
            williams_r = self.calculate_williams_r(high, low, close).iloc[-1]
            momentum = self.calculate_momentum(close).iloc[-1]
            roc = self.calculate_roc(close).iloc[-1]
            cci = self.calculate_cci(high, low, close).iloc[-1]
            obv = self.calculate_obv(close, volume).iloc[-1]
            mfi = self.calculate_mfi(high, low, close, volume).iloc[-1]
            vwap = self.calculate_vwap(high, low, close, volume).iloc[-1]

            return TechnicalIndicators(
                rsi=rsi.iloc[-1],
                macd=macd.iloc[-1],
                macd_signal=macd_signal.iloc[-1],
                macd_histogram=macd_histogram.iloc[-1],
                bollinger_upper=bollinger_upper.iloc[-1],
                bollinger_lower=bollinger_lower.iloc[-1],
                bollinger_middle=bollinger_middle.iloc[-1],
                sma_20=sma_20,
                sma_50=sma_50,
                ema_12=ema_12,
                ema_26=ema_26,
                stoch_k=stoch_k.iloc[-1],
                stoch_d=stoch_d.iloc[-1],
                atr=atr,
                adx=adx,
                williams_r=williams_r,
                momentum=momentum,
                roc=roc,
                cci=cci,
                obv=obv,
                mfi=mfi,
                vwap=vwap
            )
        except Exception as e:
            logger.error(f"Error calculating indicators for {instrument}: {e}")
            return None
    
    def generate_signals(self, indicators: TechnicalIndicators, price: float) -> MarketSignal:
        """Generate trading signals based on technical indicators"""
        signals = []
        reasoning = []
        confidence = 0.0
        
        # RSI signals
        if indicators.rsi < 30:
            signals.append(1)  # Oversold - buy signal
            reasoning.append("RSI oversold")
            confidence += 0.15
        elif indicators.rsi > 70:
            signals.append(-1)  # Overbought - sell signal
            reasoning.append("RSI overbought")
            confidence += 0.15
        
        # MACD signals
        if indicators.macd > indicators.macd_signal and indicators.macd_histogram > 0:
            signals.append(1)
            reasoning.append("MACD bullish")
            confidence += 0.2
        elif indicators.macd < indicators.macd_signal and indicators.macd_histogram < 0:
            signals.append(-1)
            reasoning.append("MACD bearish")
            confidence += 0.2
        
        # Bollinger Bands signals
        if price <= indicators.bollinger_lower:
            signals.append(1)
            reasoning.append("Price at lower Bollinger Band")
            confidence += 0.1
        elif price >= indicators.bollinger_upper:
            signals.append(-1)
            reasoning.append("Price at upper Bollinger Band")
            confidence += 0.1
        
        # Moving average signals
        if indicators.sma_20 > indicators.sma_50 and price > indicators.sma_20:
            signals.append(1)
            reasoning.append("Price above rising MA")
            confidence += 0.15
        elif indicators.sma_20 < indicators.sma_50 and price < indicators.sma_20:
            signals.append(-1)
            reasoning.append("Price below falling MA")
            confidence += 0.15
        
        # Stochastic signals
        if indicators.stoch_k < 20 and indicators.stoch_d < 20:
            signals.append(1)
            reasoning.append("Stochastic oversold")
            confidence += 0.1
        elif indicators.stoch_k > 80 and indicators.stoch_d > 80:
            signals.append(-1)
            reasoning.append("Stochastic overbought")
            confidence += 0.1
        
        # Final signal determination
        if not signals:
            signal = "HOLD"
            final_confidence = 0.0
        else:
            signal_sum = sum(signals)
            if signal_sum > 0:
                signal = "BUY"
            elif signal_sum < 0:
                signal = "SELL"
            else:
                signal = "HOLD"
            
            final_confidence = min(confidence, 1.0)
        
        strength = abs(sum(signals)) / max(len(signals), 1) if signals else 0
        
        return MarketSignal(
            signal=signal,
            confidence=final_confidence,
            strength=strength,
            reasoning=reasoning,
            indicators=indicators,
            timestamp=datetime.now()
        )
    
    def analyze_trend(self, instrument: str) -> str:
        """Analyze price trend"""
        df = self.get_price_dataframe(instrument)
        if df is None or len(df) < 20:
            return "UNKNOWN"
        
        prices = df['mid']
        sma_short = prices.rolling(10).mean().iloc[-1]
        sma_medium = prices.rolling(20).mean().iloc[-1]
        sma_long = prices.rolling(50).mean().iloc[-1]
        
        if sma_short > sma_medium > sma_long:
            return "UPTREND"
        elif sma_short < sma_medium < sma_long:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def calculate_support_resistance(self, instrument: str, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        df = self.get_price_dataframe(instrument)
        if df is None or len(df) < window * 2:
            return {}
        
        prices = df['mid'].values
        highs = []
        lows = []
        
        for i in range(window, len(prices) - window):
            if prices[i] == max(prices[i-window:i+window]):
                highs.append(prices[i])
            if prices[i] == min(prices[i-window:i+window]):
                lows.append(prices[i])
        
        if not highs or not lows:
            return {}
        
        return {
            'resistance': np.mean(highs),
            'support': np.mean(lows),
            'current_price': prices[-1]
        }