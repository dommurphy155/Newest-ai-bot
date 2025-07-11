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
        
        # ML-like features
        self.price_history = {inst: deque(maxlen=100) for inst in self.instruments.keys()}
        self.sentiment_history = deque(maxlen=50)
        self.market_regime = 'NORMAL'  # NORMAL, VOLATILE, TRENDING
        
        logger.info("Advanced Trader initialized with ML features")

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
        """Calculate advanced trading signals"""
        try:
            # Get news sentiment
            sentiment = await self.scraper.get_sentiment() if self.scraper else 0.5
            self.sentiment_history.append(sentiment)
            
            # Technical signals
            tech_score = 0.0
            
            # Trend following
            if price_data['trend'] == 'UP':
                tech_score += 0.3
            elif price_data['trend'] == 'DOWN':
                tech_score -= 0.3
            
            # Momentum
            if price_data['momentum'] > 0.001:
                tech_score += 0.2
            elif price_data['momentum'] < -0.001:
                tech_score -= 0.2
            
            # Volatility filter
            if price_data['volatility'] > self.instruments[instrument]['volatility_threshold']:
                tech_score *= 0.5  # Reduce signal strength in high volatility
            
            # Sentiment influence
            sentiment_influence = (sentiment - 0.5) * 0.4
            
            # Combine signals
            total_score = tech_score + sentiment_influence
            
            # Determine signal
            if total_score > 0.4:
                signal = 'BUY'
                confidence = min(abs(total_score), 0.95)
            elif total_score < -0.4:
                signal = 'SELL'
                confidence = min(abs(total_score), 0.95)
            else:
                signal = 'HOLD'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': confidence,
                'tech_score': tech_score,
                'sentiment_score': sentiment_influence,
                'total_score': total_score,
                'market_regime': self.market_regime
            }
            
        except Exception as e:
            logger.error(f"Error calculating signals for {instrument}: {e}")
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
                trade_info = {
                    'timestamp': datetime.now().isoformat(),
                    'instrument': instrument,
                    'side': side,
                    'units': abs(units),
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': analysis.get('confidence', 0.5),
                    'market_regime': self.market_regime
                }
                
                self.trade_history.append(trade_info)
                self.trade_count += 1
                
                logger.info(f"Trade executed: {instrument} {side} {abs(units)} units @ {current_price:.5f}")
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
                
                # Adaptive sleep based on market regime
                sleep_time = {
                    'VOLATILE': 15,
                    'TRENDING': 30,
                    'NORMAL': 45
                }.get(self.market_regime, 30)
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(30)

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
            'exposure': exposure
        }

    async def run(self):
        """Run the advanced trader"""
        try:
            self.running = True
            logger.info("Advanced Trader started with ML features")
            
            # Initial setup
            balance = await self.get_balance()
            if balance is None:
                logger.error("Failed to get initial balance")
                return
            
            logger.info(f"Initial balance: ${balance:.2f}")
            logger.info(f"Market regime: {self.market_regime}")
            
            # Start trading loop
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"Error running advanced trader: {e}")
            raise

    def stop(self):
        """Stop the trader"""
        self.running = False
        logger.info("Advanced Trader stopped")