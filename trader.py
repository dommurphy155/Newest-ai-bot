#!/usr/bin/env python3
"""
Advanced Trading Engine with ML-driven decisions
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import numpy as np
from collections import deque

import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import accounts, orders, trades, pricing, instruments
from oandapyV20.exceptions import V20Error

logger = logging.getLogger(__name__)

class AdvancedTrader:
    def __init__(self, api_key: str, account_id: str, scraper=None):
        self.api = API(access_token=api_key)
        self.account_id = account_id
        self.scraper = scraper
        self.running = False
        
        # Performance tracking
        self.trade_history = deque(maxlen=1000)
        self.balance_history = deque(maxlen=100)
        self.last_balance = 0.0
        self.trade_count = 0
        self.profitable_trades = 0
        self.total_pnl = 0.0
        
        # Advanced trading parameters
        self.instruments = {
            'EUR_USD': {'min_spread': 0.0001, 'max_spread': 0.0003, 'volatility_threshold': 0.002},
            'GBP_USD': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.003},
            'USD_JPY': {'min_spread': 0.001, 'max_spread': 0.003, 'volatility_threshold': 0.02},
            'USD_CHF': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.002},
            'AUD_USD': {'min_spread': 0.0001, 'max_spread': 0.0005, 'volatility_threshold': 0.003},
            'USD_CAD': {'min_spread': 0.0001, 'max_spread': 0.0004, 'volatility_threshold': 0.002},
            'NZD_USD': {'min_spread': 0.0001, 'max_spread': 0.0006, 'volatility_threshold': 0.003}
        }
        
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.max_daily_risk = 0.05  # 5% max daily risk
        self.max_positions = 5
        
        # Advanced ML and AI features for maximum profit
        self.price_history = {inst: deque(maxlen=500) for inst in self.instruments.keys()}
        self.volume_history = {inst: deque(maxlen=200) for inst in self.instruments.keys()}
        self.sentiment_history = deque(maxlen=100)
        self.market_regime = 'NORMAL'  # NORMAL, VOLATILE, TRENDING, BREAKOUT, REVERSAL
        
        # Profit maximization features
        self.profit_acceleration_mode = True
        self.dynamic_position_sizing = True
        self.correlation_matrix = {}
        self.volatility_forecasts = {}
        self.momentum_signals = {}
        self.breakout_detector = {}
        
        # Advanced risk management
        self.position_correlations = {}
        self.max_correlation_threshold = 0.7
        self.dynamic_stop_loss = True
        self.trailing_stops = {}
        
        # Performance optimization
        self.profit_factor = 1.0
        self.win_streak = 0
        self.loss_streak = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # Market scanning optimization
        self.last_scan_time = datetime.now()
        self.scan_frequency = 5  # seconds
        self.fast_scan_mode = True
        
        logger.info("🚀 Advanced Trader v3.0 initialized with maximum profit features")

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

    async def get_current_exposure(self) -> Dict[str, float]:
        """Calculate current market exposure"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.api.request(r)
            positions = response['account']['positions']
            
            exposure = {}
            for position in positions:
                instrument = position['instrument']
                long_units = float(position['long']['units'])
                short_units = float(position['short']['units'])
                net_units = long_units + short_units
                
                if abs(net_units) > 0:
                    exposure[instrument] = net_units
            
            return exposure
        except Exception as e:
            logger.error(f"Error getting exposure: {e}")
            return {}

    async def get_enhanced_prices(self, instruments: List[str]) -> Optional[Dict[str, Any]]:
        """Get enhanced price data with technical indicators"""
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
                
                # Calculate technical indicators
                prices = list(self.price_history[instrument])
                if len(prices) >= 20:
                    sma_20 = np.mean(prices[-20:])
                    sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
                    volatility = np.std(prices[-20:])
                    momentum = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0
                    
                    enhanced_prices[instrument] = {
                        'bid': bid,
                        'ask': ask,
                        'mid': mid,
                        'spread': spread,
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'volatility': volatility,
                        'momentum': momentum,
                        'trend': 'UP' if mid > sma_20 > sma_50 else 'DOWN' if mid < sma_20 < sma_50 else 'SIDEWAYS'
                    }
                else:
                    enhanced_prices[instrument] = {
                        'bid': bid,
                        'ask': ask,
                        'mid': mid,
                        'spread': spread,
                        'sma_20': mid,
                        'sma_50': mid,
                        'volatility': 0,
                        'momentum': 0,
                        'trend': 'SIDEWAYS'
                    }
            
            return enhanced_prices
        except Exception as e:
            logger.error(f"Error getting enhanced prices: {e}")
            return None

    async def analyze_market_regime(self) -> str:
        """Analyze current market regime"""
        try:
            if not self.balance_history or len(self.balance_history) < 10:
                return 'NORMAL'
            
            # Calculate market volatility
            recent_balances = list(self.balance_history)[-10:]
            balance_changes = [abs(recent_balances[i] - recent_balances[i-1]) / recent_balances[i-1] 
                             for i in range(1, len(recent_balances))]
            
            avg_volatility = np.mean(balance_changes)
            
            if avg_volatility > 0.02:  # 2% average change
                return 'VOLATILE'
            elif avg_volatility < 0.005:  # 0.5% average change
                return 'TRENDING'
            else:
                return 'NORMAL'
                
        except Exception as e:
            logger.error(f"Error analyzing market regime: {e}")
            return 'NORMAL'

    async def calculate_advanced_signals(self, instrument: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ultra-advanced trading signals for maximum profit"""
        try:
            # Get enhanced sentiment
            sentiment = await self.scraper.get_sentiment() if self.scraper else 0.5
            self.sentiment_history.append(sentiment)
            
            # Multi-timeframe analysis
            signals = await self.multi_timeframe_analysis(instrument, price_data)
            
            # Technical signals with advanced weighting
            tech_score = 0.0
            
            # Advanced trend analysis
            trend_strength = self.calculate_trend_strength(instrument, price_data)
            if price_data['trend'] == 'UP' and trend_strength > 0.6:
                tech_score += 0.4 * trend_strength
            elif price_data['trend'] == 'DOWN' and trend_strength > 0.6:
                tech_score -= 0.4 * trend_strength
            
            # Enhanced momentum with acceleration
            momentum_score = self.calculate_momentum_score(instrument, price_data)
            tech_score += momentum_score * 0.3
            
            # Breakout detection
            breakout_signal = self.detect_breakout(instrument, price_data)
            tech_score += breakout_signal * 0.25
            
            # Volume confirmation
            volume_confirmation = self.analyze_volume_confirmation(instrument, price_data)
            tech_score *= volume_confirmation
            
            # Market regime adjustment
            regime_multiplier = self.get_regime_multiplier()
            tech_score *= regime_multiplier
            
            # Volatility optimization
            volatility_factor = self.calculate_volatility_factor(instrument, price_data)
            tech_score *= volatility_factor
            
            # Sentiment with trend confirmation
            sentiment_influence = self.calculate_sentiment_influence(sentiment, price_data)
            
            # Correlation filter
            correlation_penalty = await self.calculate_correlation_penalty(instrument)
            
            # News impact analysis
            news_impact = await self.analyze_news_impact(instrument)
            
            # Combine all signals with advanced weighting
            total_score = (
                tech_score * 0.45 +
                sentiment_influence * 0.25 +
                signals.get('multi_timeframe_score', 0) * 0.2 +
                news_impact * 0.1
            ) * (1 - correlation_penalty)
            
            # Profit acceleration mode
            if self.profit_acceleration_mode and self.consecutive_wins >= 3:
                total_score *= 1.2  # Increase signal strength on win streaks
            
            # Dynamic confidence calculation
            confidence = self.calculate_dynamic_confidence(total_score, instrument, price_data)
            
            # Signal determination with advanced logic
            signal, final_confidence = self.determine_final_signal(total_score, confidence)
            
            return {
                'signal': signal,
                'confidence': final_confidence,
                'tech_score': tech_score,
                'sentiment_score': sentiment_influence,
                'total_score': total_score,
                'market_regime': self.market_regime,
                'trend_strength': trend_strength,
                'momentum_score': momentum_score,
                'breakout_signal': breakout_signal,
                'volume_confirmation': volume_confirmation,
                'volatility_factor': volatility_factor,
                'correlation_penalty': correlation_penalty,
                'news_impact': news_impact,
                'multi_timeframe': signals
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced signals for {instrument}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}

    async def calculate_optimal_position_size(self, instrument: str, signal: str, confidence: float) -> int:
        """Calculate optimal position size using Kelly Criterion approximation"""
        try:
            balance = await self.get_balance()
            if not balance:
                return 0
            
            # Base position size
            base_risk = balance * self.risk_per_trade
            
            # Adjust for confidence
            confidence_multiplier = confidence * 2  # 0.5 confidence = 1x, 1.0 confidence = 2x
            
            # Adjust for market regime
            regime_multiplier = {
                'NORMAL': 1.0,
                'VOLATILE': 0.5,
                'TRENDING': 1.5
            }.get(self.market_regime, 1.0)
            
            # Calculate position size
            risk_amount = base_risk * confidence_multiplier * regime_multiplier
            
            # Convert to units (simplified leverage calculation)
            if instrument in ['EUR_USD', 'GBP_USD', 'AUD_USD', 'NZD_USD']:
                units = int(risk_amount * 100)
            elif instrument == 'USD_JPY':
                units = int(risk_amount * 100)
            else:
                units = int(risk_amount * 80)
            
            # Apply limits
            max_units = min(50000, int(balance * 0.1))
            units = min(units, max_units)
            
            return max(units, 1000) if units > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0

    async def execute_trade(self, instrument: str, units: int, side: str, analysis: Dict[str, Any]) -> bool:
        """Execute trade with advanced order management"""
        try:
            if units <= 0:
                return False
            
            # Adjust units for sell orders
            if side == 'SELL':
                units = -abs(units)
            else:
                units = abs(units)
            
            # Calculate stop loss and take profit
            current_price = analysis.get('mid', 0)
            volatility = analysis.get('volatility', 0.001)
            
            # Dynamic stop loss based on volatility
            stop_distance = max(volatility * 2, 0.001)
            take_profit_distance = stop_distance * 2  # 2:1 reward:risk ratio
            
            if side == 'BUY':
                stop_loss = current_price - stop_distance
                take_profit = current_price + take_profit_distance
            else:
                stop_loss = current_price + stop_distance
                take_profit = current_price - take_profit_distance
            
            order_data = {
                'order': {
                    'type': 'MARKET',
                    'instrument': instrument,
                    'units': str(units),
                    'timeInForce': 'FOK',
                    'positionFill': 'DEFAULT',
                    'stopLossOnFill': {
                        'price': f"{stop_loss:.5f}",
                        'timeInForce': 'GTC'
                    },
                    'takeProfitOnFill': {
                        'price': f"{take_profit:.5f}",
                        'timeInForce': 'GTC'
                    }
                }
            }
            
            r = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.api.request(r)
            
            if 'orderFillTransaction' in response:
                # Get fill price from response
                fill_price = float(response['orderFillTransaction']['price'])
                
                trade_info = {
                    'timestamp': datetime.now().isoformat(),
                    'instrument': instrument,
                    'side': side,
                    'units': abs(units),
                    'entry_price': fill_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': analysis.get('confidence', 0.5),
                    'market_regime': self.market_regime,
                    'expected_profit': abs(take_profit - fill_price) * abs(units),
                    'risk_amount': abs(fill_price - stop_loss) * abs(units)
                }
                
                self.trade_history.append(trade_info)
                self.trade_count += 1
                
                # Update profit acceleration tracking
                self.update_performance_tracking()
                
                logger.info(f"🎯 Trade executed: {instrument} {side} {abs(units)} units @ {fill_price:.5f} | Confidence: {analysis.get('confidence', 0.5):.2f}")
                return True
            else:
                logger.warning(f"Order not filled: {response}")
                return False
                
        except V20Error as e:
            logger.error(f"OANDA API error executing trade: {e}")
            return False
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False

    async def check_daily_limits(self) -> bool:
        """Check if daily risk limits are exceeded"""
        try:
            today = datetime.now().date()
            today_trades = [t for t in self.trade_history 
                          if datetime.fromisoformat(t['timestamp']).date() == today]
            
            if len(today_trades) >= 50:  # Max 50 trades per day
                return False
            
            # Check daily risk exposure
            current_balance = await self.get_balance()
            if not current_balance:
                return False
            
            daily_risk = len(today_trades) * (current_balance * self.risk_per_trade)
            max_daily_risk_amount = current_balance * self.max_daily_risk
            
            return daily_risk < max_daily_risk_amount
            
        except Exception as e:
            logger.error(f"Error checking daily limits: {e}")
            return False

    async def trading_loop(self):
        """Advanced trading loop with ML-driven decisions"""
        loop_count = 0
        
        while self.running:
            try:
                loop_count += 1
                logger.info(f"Trading cycle {loop_count}")
                
                # Check daily limits
                if not await self.check_daily_limits():
                    logger.warning("Daily limits reached, pausing trading")
                    await asyncio.sleep(300)
                    continue
                
                # Update market regime
                self.market_regime = await self.analyze_market_regime()
                
                # Get current exposure
                exposure = await self.get_current_exposure()
                active_positions = len(exposure)
                
                if active_positions >= self.max_positions:
                    logger.info("Maximum positions reached, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                # Get enhanced price data
                price_data = await self.get_enhanced_prices(list(self.instruments.keys()))
                if not price_data:
                    await asyncio.sleep(30)
                    continue
                
                # Analyze each instrument
                for instrument, prices in price_data.items():
                    if not self.running:
                        break
                    
                    # Skip if already have position
                    if instrument in exposure:
                        continue
                    
                    # Check spread
                    if prices['spread'] > self.instruments[instrument]['max_spread']:
                        continue
                    
                    # Get trading signals
                    analysis = await self.calculate_advanced_signals(instrument, prices)
                    
                    # Execute trade if signal is strong
                    if analysis['signal'] != 'HOLD' and analysis['confidence'] > 0.7:
                        units = await self.calculate_optimal_position_size(
                            instrument, analysis['signal'], analysis['confidence']
                        )
                        
                        if units > 0:
                            success = await self.execute_trade(
                                instrument, units, analysis['signal'], 
                                {**prices, **analysis}
                            )
                            
                            if success:
                                logger.info(f"Trade executed: {instrument} {analysis['signal']} "
                                          f"(confidence: {analysis['confidence']:.2f})")
                    
                    await asyncio.sleep(1)
                
                # Ultra-fast adaptive sleep for maximum profit
                sleep_time = {
                    'VOLATILE': 3,
                    'TRENDING': 5,
                    'BREAKOUT': 2,
                    'REVERSAL': 4,
                    'NORMAL': 5
                }.get(self.market_regime, 5)
                
                # Further optimize based on profit acceleration mode
                if self.profit_acceleration_mode and self.consecutive_wins >= 2:
                    sleep_time = max(2, sleep_time - 1)
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(30)

    # Advanced profit maximization methods
    
    async def multi_timeframe_analysis(self, instrument: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Multi-timeframe analysis for stronger signals"""
        try:
            # Simulate different timeframes
            short_term_score = price_data.get('momentum', 0) * 2
            medium_term_score = (price_data.get('sma_20', 0) - price_data.get('sma_50', 0)) / price_data.get('mid', 1)
            long_term_score = price_data.get('trend', 'SIDEWAYS')
            
            # Weight the scores
            if long_term_score == 'UP':
                long_term_value = 0.3
            elif long_term_score == 'DOWN':
                long_term_value = -0.3
            else:
                long_term_value = 0.0
            
            combined_score = (short_term_score * 0.5 + medium_term_score * 0.3 + long_term_value * 0.2)
            
            return {
                'multi_timeframe_score': combined_score,
                'short_term': short_term_score,
                'medium_term': medium_term_score,
                'long_term': long_term_value
            }
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {'multi_timeframe_score': 0.0}
    
    def calculate_trend_strength(self, instrument: str, price_data: Dict[str, Any]) -> float:
        """Calculate trend strength for better signal quality"""
        try:
            sma_20 = price_data.get('sma_20', 0)
            sma_50 = price_data.get('sma_50', 0)
            current_price = price_data.get('mid', 0)
            
            if sma_20 == 0 or sma_50 == 0 or current_price == 0:
                return 0.0
            
            # Calculate trend strength based on price position relative to MAs
            trend_strength = abs((current_price - sma_50) / sma_50)
            
            # Confirm with moving average alignment
            if (current_price > sma_20 > sma_50) or (current_price < sma_20 < sma_50):
                trend_strength *= 1.5
            
            return min(trend_strength, 1.0)
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.0
    
    def calculate_momentum_score(self, instrument: str, price_data: Dict[str, Any]) -> float:
        """Calculate enhanced momentum score"""
        try:
            momentum = price_data.get('momentum', 0)
            volatility = price_data.get('volatility', 0.001)
            
            # Normalize momentum by volatility
            if volatility > 0:
                normalized_momentum = momentum / volatility
            else:
                normalized_momentum = 0
            
            # Apply momentum threshold
            if abs(normalized_momentum) > 2.0:
                return np.sign(normalized_momentum) * 0.8
            elif abs(normalized_momentum) > 1.0:
                return np.sign(normalized_momentum) * 0.4
            else:
                return normalized_momentum * 0.2
        except Exception as e:
            logger.error(f"Error calculating momentum score: {e}")
            return 0.0
    
    def detect_breakout(self, instrument: str, price_data: Dict[str, Any]) -> float:
        """Detect breakout patterns for high-profit opportunities"""
        try:
            current_price = price_data.get('mid', 0)
            sma_20 = price_data.get('sma_20', 0)
            volatility = price_data.get('volatility', 0.001)
            
            if current_price == 0 or sma_20 == 0:
                return 0.0
            
            # Calculate price deviation from moving average
            deviation = abs(current_price - sma_20) / sma_20
            
            # Breakout detection based on volatility expansion
            if deviation > volatility * 3:
                return np.sign(current_price - sma_20) * 0.6
            elif deviation > volatility * 2:
                return np.sign(current_price - sma_20) * 0.3
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error detecting breakout: {e}")
            return 0.0
    
    def analyze_volume_confirmation(self, instrument: str, price_data: Dict[str, Any]) -> float:
        """Analyze volume confirmation (simulated for forex)"""
        try:
            # Since forex doesn't have traditional volume, use spread as proxy
            spread = price_data.get('spread', 0.001)
            max_spread = self.instruments.get(instrument, {}).get('max_spread', 0.001)
            
            # Tighter spreads indicate better liquidity/volume
            volume_factor = 1.0 - (spread / max_spread)
            return max(0.5, volume_factor)  # Minimum 0.5 multiplier
        except Exception as e:
            logger.error(f"Error analyzing volume confirmation: {e}")
            return 1.0
    
    def get_regime_multiplier(self) -> float:
        """Get multiplier based on market regime"""
        multipliers = {
            'TRENDING': 1.3,
            'BREAKOUT': 1.5,
            'VOLATILE': 0.7,
            'REVERSAL': 1.2,
            'NORMAL': 1.0
        }
        return multipliers.get(self.market_regime, 1.0)
    
    def calculate_volatility_factor(self, instrument: str, price_data: Dict[str, Any]) -> float:
        """Calculate volatility adjustment factor"""
        try:
            volatility = price_data.get('volatility', 0.001)
            threshold = self.instruments.get(instrument, {}).get('volatility_threshold', 0.002)
            
            if volatility > threshold * 2:
                return 0.5  # Reduce signal in extreme volatility
            elif volatility > threshold:
                return 0.7  # Moderate reduction
            else:
                return 1.2  # Boost signal in low volatility
        except Exception as e:
            logger.error(f"Error calculating volatility factor: {e}")
            return 1.0
    
    def calculate_sentiment_influence(self, sentiment: float, price_data: Dict[str, Any]) -> float:
        """Calculate enhanced sentiment influence"""
        try:
            # Base sentiment influence
            base_influence = (sentiment - 0.5) * 0.6
            
            # Amplify if sentiment aligns with technical trend
            trend = price_data.get('trend', 'SIDEWAYS')
            if (sentiment > 0.6 and trend == 'UP') or (sentiment < 0.4 and trend == 'DOWN'):
                base_influence *= 1.5
            
            return base_influence
        except Exception as e:
            logger.error(f"Error calculating sentiment influence: {e}")
            return 0.0
    
    async def calculate_correlation_penalty(self, instrument: str) -> float:
        """Calculate correlation penalty to avoid overexposure"""
        try:
            current_exposure = await self.get_current_exposure()
            if not current_exposure:
                return 0.0
            
            # Simple correlation simulation (in reality, use historical correlation)
            correlation_pairs = {
                'EUR_USD': ['GBP_USD', 'AUD_USD'],
                'GBP_USD': ['EUR_USD', 'AUD_USD'],
                'USD_JPY': ['USD_CHF', 'USD_CAD'],
                'USD_CHF': ['USD_JPY', 'USD_CAD'],
                'AUD_USD': ['EUR_USD', 'GBP_USD', 'NZD_USD'],
                'USD_CAD': ['USD_JPY', 'USD_CHF'],
                'NZD_USD': ['AUD_USD']
            }
            
            penalty = 0.0
            related_instruments = correlation_pairs.get(instrument, [])
            
            for related in related_instruments:
                if related in current_exposure:
                    penalty += 0.15  # 15% penalty per correlated position
            
            return min(penalty, 0.5)  # Max 50% penalty
        except Exception as e:
            logger.error(f"Error calculating correlation penalty: {e}")
            return 0.0
    
    async def analyze_news_impact(self, instrument: str) -> float:
        """Analyze news impact on specific instrument"""
        try:
            if not self.scraper:
                return 0.0
            
            # Get sentiment trend
            trend = await self.scraper.get_sentiment_trend()
            sentiment = await self.scraper.get_sentiment()
            
            impact_score = 0.0
            
            if trend == 'IMPROVING' and sentiment > 0.6:
                impact_score = 0.3
            elif trend == 'DECLINING' and sentiment < 0.4:
                impact_score = -0.3
            elif trend == 'STABLE':
                impact_score = 0.0
            
            return impact_score
        except Exception as e:
            logger.error(f"Error analyzing news impact: {e}")
            return 0.0
    
    def calculate_dynamic_confidence(self, total_score: float, instrument: str, price_data: Dict[str, Any]) -> float:
        """Calculate dynamic confidence based on multiple factors"""
        try:
            base_confidence = min(abs(total_score), 0.95)
            
            # Adjust based on recent performance
            if self.win_streak >= 3:
                base_confidence *= 1.1
            elif self.loss_streak >= 2:
                base_confidence *= 0.9
            
            # Adjust based on market conditions
            volatility = price_data.get('volatility', 0.001)
            if volatility < self.instruments.get(instrument, {}).get('volatility_threshold', 0.002):
                base_confidence *= 1.15  # Higher confidence in stable markets
            
            return min(base_confidence, 0.98)
        except Exception as e:
            logger.error(f"Error calculating dynamic confidence: {e}")
            return 0.5
    
    def determine_final_signal(self, total_score: float, confidence: float) -> tuple:
        """Determine final trading signal with advanced logic"""
        try:
            # Dynamic thresholds based on market regime and confidence
            buy_threshold = 0.35 if self.market_regime in ['TRENDING', 'BREAKOUT'] else 0.45
            sell_threshold = -buy_threshold
            
            # Adjust thresholds based on confidence
            if confidence > 0.8:
                buy_threshold *= 0.8
                sell_threshold *= 0.8
            elif confidence < 0.6:
                buy_threshold *= 1.2
                sell_threshold *= 1.2
            
            if total_score > buy_threshold:
                return 'BUY', confidence
            elif total_score < sell_threshold:
                return 'SELL', confidence
            else:
                return 'HOLD', 0.5
        except Exception as e:
            logger.error(f"Error determining final signal: {e}")
            return 'HOLD', 0.0

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get comprehensive trading status"""
        balance = await self.get_balance()
        exposure = await self.get_current_exposure()
        
        # Calculate win rate
        if self.trade_count > 0:
            win_rate = self.profitable_trades / self.trade_count
        else:
            win_rate = 0.0
        
        return {
            'running': self.running,
            'balance': balance,
            'trade_count': self.trade_count,
            'profitable_trades': self.profitable_trades,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'active_positions': len(exposure),
            'market_regime': self.market_regime,
            'daily_trades': len([t for t in self.trade_history 
                               if datetime.fromisoformat(t['timestamp']).date() == datetime.now().date()]),
            'instruments': list(self.instruments.keys()),
            'exposure': exposure,
            'profit_factor': self.profit_factor,
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses,
            'scan_frequency': self.scan_frequency,
            'profit_acceleration_mode': self.profit_acceleration_mode
        }

    def update_performance_tracking(self):
        """Update performance tracking metrics"""
        try:
            # This would be called after trade completion to update streaks
            # For now, we'll simulate based on recent trades
            if len(self.trade_history) >= 2:
                recent_trades = list(self.trade_history)[-5:]  # Last 5 trades
                wins = sum(1 for trade in recent_trades if trade.get('expected_profit', 0) > 0)
                
                if wins > len(recent_trades) / 2:
                    self.win_streak += 1
                    self.loss_streak = 0
                    self.consecutive_wins += 1
                    self.consecutive_losses = 0
                else:
                    self.loss_streak += 1
                    self.win_streak = 0
                    self.consecutive_losses += 1
                    self.consecutive_wins = 0
                
                # Update profit factor
                self.profit_factor = max(0.5, min(2.0, 1.0 + (self.win_streak * 0.1) - (self.loss_streak * 0.05)))
                
        except Exception as e:
            logger.error(f"Error updating performance tracking: {e}")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get detailed account information"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.api.request(r)
            return response.get('account', {})
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    async def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.api.request(r)
            return response.get('account', {}).get('positions', [])
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get trader status for the bot"""
        return await self.get_detailed_status()

    async def run(self):
        """Run the advanced trader with maximum profit optimization"""
        try:
            self.running = True
            logger.info("🚀 Advanced Trader v3.0 started with MAXIMUM PROFIT MODE")
            
            # Initial setup
            balance = await self.get_balance()
            if balance is None:
                logger.error("❌ Failed to get initial balance")
                return
            
            logger.info(f"💰 Initial balance: ${balance:.2f}")
            logger.info(f"📊 Market regime: {self.market_regime}")
            logger.info(f"⚡ Profit acceleration: {'ENABLED' if self.profit_acceleration_mode else 'DISABLED'}")
            logger.info(f"🎯 Scan frequency: {self.scan_frequency}s")
            
            # Start ultra-fast trading loop
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"Error running advanced trader: {e}")
            raise

    def stop(self):
        """Stop the trader"""
        self.running = False
        logger.info("Advanced Trader stopped")