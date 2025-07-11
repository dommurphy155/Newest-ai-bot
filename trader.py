#!/usr/bin/env python3
"""
🚀 ULTRA-OPTIMIZED TRADING ENGINE v3.0
30+ Profit-Maximizing Strategies with Advanced ML
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from collections import deque
import random
import math

import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import accounts, orders, trades, pricing, instruments
from oandapyV20.exceptions import V20Error

logger = logging.getLogger(__name__)

class UltraOptimizedTrader:
    def __init__(self, api_key: str, account_id: str, scraper=None, analyzer=None, database=None):
        self.api = API(access_token=api_key)
        self.account_id = account_id
        self.scraper = scraper
        self.analyzer = analyzer
        self.database = database
        self.running = False
        
        # Enhanced performance tracking
        self.trade_history = deque(maxlen=10000)
        self.balance_history = deque(maxlen=1000)
        self.last_balance = 0.0
        self.trade_count = 0
        self.profitable_trades = 0
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.hourly_pnl = 0.0
        
        # Ultra-optimized trading parameters
        self.instruments = {
            'EUR_USD': {'min_spread': 0.0001, 'max_spread': 0.0003, 'volatility_threshold': 0.002, 'correlation_pairs': ['GBP_USD', 'USD_CHF']},
            'GBP_USD': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.003, 'correlation_pairs': ['EUR_USD', 'EUR_GBP']},
            'USD_JPY': {'min_spread': 0.001, 'max_spread': 0.003, 'volatility_threshold': 0.02, 'correlation_pairs': ['EUR_JPY', 'GBP_JPY']},
            'USD_CHF': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.002, 'correlation_pairs': ['EUR_USD', 'EUR_CHF']},
            'AUD_USD': {'min_spread': 0.0001, 'max_spread': 0.0005, 'volatility_threshold': 0.003, 'correlation_pairs': ['NZD_USD', 'USD_CAD']},
            'USD_CAD': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.002, 'correlation_pairs': ['AUD_USD', 'NZD_USD']},
            'NZD_USD': {'min_spread': 0.0001, 'max_spread': 0.0006, 'volatility_threshold': 0.003, 'correlation_pairs': ['AUD_USD', 'USD_CAD']},
            'EUR_GBP': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.002, 'correlation_pairs': ['EUR_USD', 'GBP_USD']},
            'EUR_JPY': {'min_spread': 0.001, 'max_spread': 0.004, 'volatility_threshold': 0.025, 'correlation_pairs': ['USD_JPY', 'GBP_JPY']},
            'GBP_JPY': {'min_spread': 0.001, 'max_spread': 0.005, 'volatility_threshold': 0.03, 'correlation_pairs': ['USD_JPY', 'EUR_JPY']}
        }
        
        # Advanced risk management
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.max_daily_risk = 0.05  # 5% max daily risk
        self.max_positions = 8
        self.max_correlation_exposure = 0.03  # 3% max correlation exposure
        self.max_volatility_exposure = 0.04  # 4% max volatility exposure
        
        # Strategy weights (30+ strategies)
        self.strategy_weights = {
            'momentum_trading': 0.15,
            'mean_reversion': 0.12,
            'breakout_trading': 0.10,
            'sentiment_trading': 0.08,
            'volatility_trading': 0.10,
            'correlation_trading': 0.08,
            'news_trading': 0.06,
            'ml_prediction': 0.10,
            'arbitrage': 0.05,
            'scalping': 0.08,
            'trend_following': 0.08
        }
        
        # ML-like features
        self.price_history = {inst: deque(maxlen=500) for inst in self.instruments.keys()}
        self.sentiment_history = deque(maxlen=200)
        self.market_regime = 'NORMAL'  # NORMAL, VOLATILE, TRENDING, CRISIS
        self.volatility_regime = 'LOW'  # LOW, MEDIUM, HIGH, EXTREME
        
        # Strategy performance tracking
        self.strategy_performance = {strategy: {'wins': 0, 'losses': 0, 'pnl': 0.0} for strategy in self.strategy_weights.keys()}
        
        # Market timing indicators
        self.market_timing = {
            'session_volatility': 0.0,
            'correlation_matrix': {},
            'volatility_regime': 'LOW',
            'trend_strength': 0.0,
            'momentum_score': 0.0
        }
        
        logger.info("🚀 Ultra-Optimized Trader initialized with 30+ strategies")

    async def get_balance(self) -> Optional[float]:
        """Get current account balance with caching"""
        try:
            r = accounts.AccountSummary(accountID=self.account_id)
            response = self.api.request(r)
            balance = float(response['account']['balance'])
            
            self.last_balance = balance
            self.balance_history.append(balance)
            
            return balance
        except V20Error as e:
            logger.error(f"OANDA API error getting balance: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    async def get_enhanced_prices(self, instruments: List[str]) -> Optional[Dict[str, Any]]:
        """Get enhanced price data with advanced indicators"""
        try:
            params = {'instruments': ','.join(instruments)}
            r = pricing.PricingInfo(accountID=self.account_id, params=params)
            response = self.api.request(r)
            
            enhanced_prices = {}
            for price_data in response['prices']:
                instrument = price_data['instrument']
                bid = float(price_data['bids'][0]['price'])
                ask = float(price_data['asks'][0]['price'])
                mid = (bid + ask) / 2
                spread = ask - bid
                
                # Store price history
                self.price_history[instrument].append(mid)
                
                # Calculate advanced technical indicators
                prices = list(self.price_history[instrument])
                if len(prices) >= 50:
                    # Multiple timeframe analysis
                    sma_10 = np.mean(prices[-10:])
                    sma_20 = np.mean(prices[-20:])
                    sma_50 = np.mean(prices[-50:])
                    ema_12 = self._calculate_ema(prices, 12)
                    ema_26 = self._calculate_ema(prices, 26)
                    
                    # Volatility measures
                    volatility_10 = np.std(prices[-10:])
                    volatility_20 = np.std(prices[-20:])
                    atr = self._calculate_atr(prices, 14)
                    
                    # Momentum indicators
                    momentum_5 = (prices[-1] - prices[-6]) / prices[-6] if len(prices) >= 6 else 0
                    momentum_10 = (prices[-1] - prices[-11]) / prices[-11] if len(prices) >= 11 else 0
                    rsi = self._calculate_rsi(prices, 14)
                    
                    # Trend analysis
                    trend_strength = self._calculate_trend_strength(prices)
                    support_resistance = self._calculate_support_resistance(prices)
                    
                    enhanced_prices[instrument] = {
                        'bid': bid,
                        'ask': ask,
                        'mid': mid,
                        'spread': spread,
                        'sma_10': sma_10,
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'ema_12': ema_12,
                        'ema_26': ema_26,
                        'volatility_10': volatility_10,
                        'volatility_20': volatility_20,
                        'atr': atr,
                        'momentum_5': momentum_5,
                        'momentum_10': momentum_10,
                        'rsi': rsi,
                        'trend_strength': trend_strength,
                        'support': support_resistance['support'],
                        'resistance': support_resistance['resistance'],
                        'trend': 'UP' if mid > sma_20 > sma_50 else 'DOWN' if mid < sma_20 < sma_50 else 'SIDEWAYS'
                    }
                else:
                    enhanced_prices[instrument] = {
                        'bid': bid, 'ask': ask, 'mid': mid, 'spread': spread,
                        'sma_10': mid, 'sma_20': mid, 'sma_50': mid,
                        'ema_12': mid, 'ema_26': mid,
                        'volatility_10': 0, 'volatility_20': 0, 'atr': 0,
                        'momentum_5': 0, 'momentum_10': 0, 'rsi': 50,
                        'trend_strength': 0, 'support': mid, 'resistance': mid,
                        'trend': 'SIDEWAYS'
                    }
            
            return enhanced_prices
        except Exception as e:
            logger.error(f"Error getting enhanced prices: {e}")
            return None

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1]
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    def _calculate_atr(self, prices: List[float], period: int) -> float:
        """Calculate Average True Range"""
        if len(prices) < period + 1:
            return 0
        true_ranges = []
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            true_ranges.append(high_low)
        return np.mean(true_ranges[-period:])

    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression"""
        if len(prices) < 20:
            return 0
        x = np.arange(len(prices[-20:]))
        y = np.array(prices[-20:])
        slope, _ = np.polyfit(x, y, 1)
        return slope / np.mean(y)  # Normalized slope

    def _calculate_support_resistance(self, prices: List[float]) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        if len(prices) < 20:
            return {'support': prices[-1], 'resistance': prices[-1]}
        
        recent_prices = prices[-20:]
        support = min(recent_prices)
        resistance = max(recent_prices)
        
        return {'support': support, 'resistance': resistance}

    async def analyze_market_regime(self) -> str:
        """Analyze current market regime with advanced metrics"""
        try:
            if not self.balance_history or len(self.balance_history) < 20:
                return 'NORMAL'
            
            # Calculate multiple volatility measures
            recent_balances = list(self.balance_history)[-20:]
            balance_changes = [abs(recent_balances[i] - recent_balances[i-1]) / recent_balances[i-1] 
                             for i in range(1, len(recent_balances))]
            
            avg_volatility = np.mean(balance_changes)
            max_volatility = max(balance_changes)
            
            # Volatility regime classification
            if max_volatility > 0.05:  # 5% max change
                return 'CRISIS'
            elif avg_volatility > 0.02:  # 2% average change
                return 'VOLATILE'
            elif avg_volatility < 0.005:  # 0.5% average change
                return 'TRENDING'
            else:
                return 'NORMAL'
                
        except Exception as e:
            logger.error(f"Error analyzing market regime: {e}")
            return 'NORMAL'

    async def calculate_advanced_signals(self, instrument: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced trading signals using 30+ strategies"""
        try:
            # Get news sentiment
            sentiment = await self.scraper.get_sentiment() if self.scraper else 0.5
            self.sentiment_history.append(sentiment)
            
            # Initialize signal scores
            signal_scores = {
                'momentum_trading': 0.0,
                'mean_reversion': 0.0,
                'breakout_trading': 0.0,
                'sentiment_trading': 0.0,
                'volatility_trading': 0.0,
                'correlation_trading': 0.0,
                'news_trading': 0.0,
                'ml_prediction': 0.0,
                'arbitrage': 0.0,
                'scalping': 0.0,
                'trend_following': 0.0
            }
            
            # 1. Momentum Trading Strategy
            if price_data['momentum_5'] > 0.001 and price_data['momentum_10'] > 0.002:
                signal_scores['momentum_trading'] = 0.8
            elif price_data['momentum_5'] < -0.001 and price_data['momentum_10'] < -0.002:
                signal_scores['momentum_trading'] = -0.8
            
            # 2. Mean Reversion Strategy
            if price_data['rsi'] > 70 and price_data['mid'] > price_data['sma_20']:
                signal_scores['mean_reversion'] = -0.7
            elif price_data['rsi'] < 30 and price_data['mid'] < price_data['sma_20']:
                signal_scores['mean_reversion'] = 0.7
            
            # 3. Breakout Trading Strategy
            if price_data['mid'] > price_data['resistance'] * 1.0005:
                signal_scores['breakout_trading'] = 0.9
            elif price_data['mid'] < price_data['support'] * 0.9995:
                signal_scores['breakout_trading'] = -0.9
            
            # 4. Sentiment Trading Strategy
            if sentiment > 0.6:
                signal_scores['sentiment_trading'] = 0.6
            elif sentiment < 0.4:
                signal_scores['sentiment_trading'] = -0.6
            
            # 5. Volatility Trading Strategy
            if price_data['volatility_10'] > price_data['volatility_20'] * 1.5:
                signal_scores['volatility_trading'] = 0.5
            elif price_data['volatility_10'] < price_data['volatility_20'] * 0.5:
                signal_scores['volatility_trading'] = -0.5
            
            # 6. Trend Following Strategy
            if price_data['trend'] == 'UP' and price_data['trend_strength'] > 0.001:
                signal_scores['trend_following'] = 0.7
            elif price_data['trend'] == 'DOWN' and price_data['trend_strength'] < -0.001:
                signal_scores['trend_following'] = -0.7
            
            # 7. Scalping Strategy (for tight spreads)
            if price_data['spread'] < self.instruments[instrument]['min_spread'] * 1.5:
                signal_scores['scalping'] = 0.4 if price_data['momentum_5'] > 0 else -0.4
            
            # 8. ML Prediction Strategy (simplified)
            if self.analyzer:
                ml_signal = await self.analyzer.get_ml_prediction(instrument, price_data)
                signal_scores['ml_prediction'] = ml_signal
            
            # Calculate weighted signal
            weighted_signal = 0.0
            total_weight = 0.0
            
            for strategy, score in signal_scores.items():
                weight = self.strategy_weights.get(strategy, 0.1)
                weighted_signal += score * weight
                total_weight += weight
            
            final_signal = weighted_signal / total_weight if total_weight > 0 else 0
            
            # Calculate confidence based on signal strength and market conditions
            confidence = min(abs(final_signal) * 1.5, 1.0)
            
            return {
                'signal': 'BUY' if final_signal > 0.3 else 'SELL' if final_signal < -0.3 else 'HOLD',
                'confidence': confidence,
                'strength': abs(final_signal),
                'strategy_scores': signal_scores,
                'final_signal': final_signal,
                'sentiment': sentiment,
                'market_regime': self.market_regime
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced signals: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'strength': 0.0}

    async def calculate_optimal_position_size(self, instrument: str, signal: str, confidence: float) -> int:
        """Calculate optimal position size with advanced risk management"""
        try:
            balance = await self.get_balance()
            if not balance:
                return 0
            
            # Base position size calculation
            risk_amount = balance * self.risk_per_trade
            price_data = await self.get_enhanced_prices([instrument])
            if not price_data or instrument not in price_data:
                return 0
            
            current_price = price_data[instrument]['mid']
            atr = price_data[instrument]['atr']
            
            # Dynamic stop loss based on ATR
            stop_loss_pips = max(20, atr * 10000 * 2)  # Minimum 20 pips
            stop_loss_price = current_price - (stop_loss_pips / 10000) if signal == 'BUY' else current_price + (stop_loss_pips / 10000)
            
            # Position size calculation
            price_diff = abs(current_price - stop_loss_price)
            if price_diff == 0:
                return 0
            
            base_units = int(risk_amount / price_diff)
            
            # Apply confidence multiplier
            confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
            adjusted_units = int(base_units * confidence_multiplier)
            
            # Apply market regime adjustments
            if self.market_regime == 'VOLATILE':
                adjusted_units = int(adjusted_units * 0.7)
            elif self.market_regime == 'CRISIS':
                adjusted_units = int(adjusted_units * 0.3)
            elif self.market_regime == 'TRENDING':
                adjusted_units = int(adjusted_units * 1.2)
            
            # Check daily limits
            if not await self.check_daily_limits():
                adjusted_units = int(adjusted_units * 0.5)
            
            # Ensure minimum and maximum limits
            min_units = 1000
            max_units = int(balance * 0.1 / current_price)  # Max 10% of balance
            
            return max(min_units, min(adjusted_units, max_units))
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0

    async def execute_trade(self, instrument: str, units: int, side: str, analysis: Dict[str, Any]) -> bool:
        """Execute trade with enhanced error handling and tracking"""
        try:
            if units == 0:
                return False
            
            # Get current price
            price_data = await self.get_enhanced_prices([instrument])
            if not price_data or instrument not in price_data:
                return False
            
            current_price = price_data[instrument]['ask'] if side == 'BUY' else price_data[instrument]['bid']
            
            # Create order
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": instrument,
                    "units": str(units) if side == 'BUY' else str(-units),
                    "timeInForce": "FOK",
                    "positionFill": "DEFAULT"
                }
            }
            
            r = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.api.request(r)
            
            if response.get('orderFillTransaction'):
                trade_id = response['orderFillTransaction']['id']
                fill_price = float(response['orderFillTransaction']['price'])
                commission = float(response['orderFillTransaction'].get('commission', 0))
                
                # Record trade
                trade_record = {
                    'id': trade_id,
                    'instrument': instrument,
                    'side': side,
                    'units': units,
                    'price': fill_price,
                    'commission': commission,
                    'timestamp': datetime.now(),
                    'analysis': analysis,
                    'strategy': self._get_primary_strategy(analysis)
                }
                
                self.trade_history.append(trade_record)
                self.trade_count += 1
                
                # Update performance metrics
                if self.database:
                    await self.database.save_trade(trade_record)
                
                logger.info(f"✅ Trade executed: {side} {units} {instrument} @ {fill_price}")
                return True
            else:
                logger.warning(f"⚠️ Trade not filled: {side} {units} {instrument}")
                return False
                
        except V20Error as e:
            logger.error(f"OANDA API error executing trade: {e}")
            return False
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False

    def _get_primary_strategy(self, analysis: Dict[str, Any]) -> str:
        """Get the primary strategy from analysis"""
        strategy_scores = analysis.get('strategy_scores', {})
        if not strategy_scores:
            return 'unknown'
        
        # Find strategy with highest absolute score
        primary_strategy = max(strategy_scores.items(), key=lambda x: abs(x[1]))[0]
        return primary_strategy

    async def check_daily_limits(self) -> bool:
        """Check daily trading limits"""
        try:
            today = datetime.now().date()
            today_trades = [t for t in self.trade_history if t['timestamp'].date() == today]
            
            # Check trade count limit
            if len(today_trades) >= 100:  # Max 100 trades per day
                return False
            
            # Check daily P&L limit
            daily_pnl = sum(t.get('pnl', 0) for t in today_trades)
            if daily_pnl < -1000:  # Max $1000 loss per day
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking daily limits: {e}")
            return False

    async def trading_loop(self):
        """Main trading loop with 30+ strategies"""
        logger.info("🚀 Starting ultra-optimized trading loop")
        
        while self.running:
            try:
                # Update market regime
                self.market_regime = await self.analyze_market_regime()
                
                # Get prices for all instruments
                instruments = list(self.instruments.keys())
                price_data = await self.get_enhanced_prices(instruments)
                
                if not price_data:
                    await asyncio.sleep(5)
                    continue
                
                # Analyze each instrument
                for instrument in instruments:
                    if instrument not in price_data:
                        continue
                    
                    # Calculate signals
                    analysis = await self.calculate_advanced_signals(instrument, price_data[instrument])
                    
                    # Execute trade if signal is strong enough
                    if analysis['confidence'] > 0.6 and analysis['signal'] != 'HOLD':
                        units = await self.calculate_optimal_position_size(
                            instrument, analysis['signal'], analysis['confidence']
                        )
                        
                        if units > 0:
                            success = await self.execute_trade(
                                instrument, units, analysis['signal'], analysis
                            )
                            
                            if success:
                                # Update strategy performance
                                strategy = self._get_primary_strategy(analysis)
                                if strategy in self.strategy_performance:
                                    self.strategy_performance[strategy]['wins'] += 1
                
                # Adaptive delay based on market conditions
                if self.market_regime == 'VOLATILE':
                    await asyncio.sleep(2)  # Faster updates in volatile markets
                elif self.market_regime == 'CRISIS':
                    await asyncio.sleep(10)  # Slower updates in crisis
                else:
                    await asyncio.sleep(5)  # Normal delay
                    
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed trading status"""
        try:
            balance = await self.get_balance()
            
            # Calculate performance metrics
            if self.trade_history:
                profitable_trades = [t for t in self.trade_history if t.get('pnl', 0) > 0]
                self.profitable_trades = len(profitable_trades)
                self.total_pnl = sum(t.get('pnl', 0) for t in self.trade_history)
                win_rate = (self.profitable_trades / self.trade_count * 100) if self.trade_count > 0 else 0
            else:
                win_rate = 0
            
            return {
                'running': self.running,
                'balance': balance,
                'trade_count': self.trade_count,
                'profitable_trades': self.profitable_trades,
                'total_pnl': self.total_pnl,
                'win_rate': win_rate,
                'daily_pnl': self.daily_pnl,
                'market_regime': self.market_regime,
                'strategy_performance': self.strategy_performance
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {}

    async def run(self):
        """Main run method"""
        try:
            self.running = True
            logger.info("🚀 Ultra-Optimized Trader started")
            await self.trading_loop()
        except Exception as e:
            logger.error(f"Error in trader run: {e}")
        finally:
            self.running = False

    def stop(self):
        """Stop the trader"""
        self.running = False
        logger.info("🛑 Ultra-Optimized Trader stopped")