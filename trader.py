#!/usr/bin/env python3
"""
Trading Logic for AI Trading Bot
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import accounts, orders, trades, pricing, instruments
from oandapyV20.exceptions import V20Error

from scraper import NewsScraper

logger = logging.getLogger(__name__)

class Trader:
    def __init__(self, api_key: str, account_id: str, hf_token: Optional[str] = None):
        self.api = API(access_token=api_key)
        self.account_id = account_id
        self.hf_token = hf_token
        self.running = False
        self.news_scraper = NewsScraper()
        self.last_balance = 0.0
        self.trade_count = 0
        
        # Trading parameters
        self.max_spread = 0.0005  # Maximum spread to trade
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.instruments = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CAD']
        
        logger.info("Trader initialized successfully")

    async def get_balance(self) -> Optional[float]:
        """Get current account balance"""
        try:
            r = accounts.AccountSummary(accountID=self.account_id)
            response = self.api.request(r)
            balance = float(response['account']['balance'])
            self.last_balance = balance
            return balance
        except V20Error as e:
            logger.error(f"OANDA API error getting balance: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get detailed account information"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.api.request(r)
            return response['account']
        except V20Error as e:
            logger.error(f"OANDA API error getting account info: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    async def get_prices(self, instruments: list) -> Optional[Dict[str, Any]]:
        """Get current prices for instruments"""
        try:
            params = {'instruments': ','.join(instruments)}
            r = pricing.PricingInfo(accountID=self.account_id, params=params)
            response = self.api.request(r)
            return response['prices']
        except V20Error as e:
            logger.error(f"OANDA API error getting prices: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting prices: {e}")
            return None

    async def analyze_market(self, instrument: str) -> Dict[str, Any]:
        """Analyze market conditions for an instrument"""
        try:
            # Get current price
            prices = await self.get_prices([instrument])
            if not prices:
                return {'signal': 'HOLD', 'confidence': 0.0}
            
            price_data = prices[0]
            bid = float(price_data['bids'][0]['price'])
            ask = float(price_data['asks'][0]['price'])
            spread = ask - bid
            
            # Check spread
            if spread > self.max_spread:
                logger.warning(f"Spread too high for {instrument}: {spread}")
                return {'signal': 'HOLD', 'confidence': 0.0}
            
            # Get news sentiment
            sentiment = await self.news_scraper.get_sentiment()
            
            # Simple trading logic (replace with your AI model)
            signal = 'HOLD'
            confidence = 0.5
            
            if sentiment > 0.6:
                signal = 'BUY'
                confidence = min(sentiment, 0.8)
            elif sentiment < 0.4:
                signal = 'SELL'
                confidence = min(1 - sentiment, 0.8)
            
            return {
                'signal': signal,
                'confidence': confidence,
                'bid': bid,
                'ask': ask,
                'spread': spread,
                'sentiment': sentiment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market for {instrument}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}

    async def calculate_position_size(self, instrument: str, signal: str) -> float:
        """Calculate position size based on risk management"""
        try:
            balance = await self.get_balance()
            if not balance:
                return 0.0
            
            # Calculate risk amount
            risk_amount = balance * self.risk_per_trade
            
            # Simple position sizing (you can make this more sophisticated)
            if instrument in ['EUR_USD', 'GBP_USD']:
                units = int(risk_amount * 100)  # 1:100 leverage approximation
            else:
                units = int(risk_amount * 50)   # 1:50 leverage approximation
            
            return min(units, 10000)  # Max 10k units per trade
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0

    async def place_order(self, instrument: str, units: int, side: str) -> bool:
        """Place a market order"""
        try:
            if units <= 0:
                return False
            
            # Adjust units for sell orders
            if side == 'SELL':
                units = -abs(units)
            else:
                units = abs(units)
            
            order_data = {
                'order': {
                    'type': 'MARKET',
                    'instrument': instrument,
                    'units': str(units),
                    'timeInForce': 'FOK',  # Fill or Kill
                    'positionFill': 'DEFAULT'
                }
            }
            
            r = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.api.request(r)
            
            if 'orderFillTransaction' in response:
                self.trade_count += 1
                logger.info(f"Order placed successfully: {instrument} {side} {units} units")
                return True
            else:
                logger.warning(f"Order not filled: {response}")
                return False
                
        except V20Error as e:
            logger.error(f"OANDA API error placing order: {e}")
            return False
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False

    async def get_open_positions(self) -> Optional[list]:
        """Get open positions"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.api.request(r)
            return response['account']['positions']
        except V20Error as e:
            logger.error(f"OANDA API error getting positions: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return None

    async def trading_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                logger.info("Running trading analysis...")
                
                # Check each instrument
                for instrument in self.instruments:
                    if not self.running:
                        break
                    
                    analysis = await self.analyze_market(instrument)
                    
                    if analysis['signal'] != 'HOLD' and analysis['confidence'] > 0.7:
                        units = await self.calculate_position_size(instrument, analysis['signal'])
                        
                        if units > 0:
                            success = await self.place_order(instrument, units, analysis['signal'])
                            if success:
                                logger.info(f"Trade executed: {instrument} {analysis['signal']} "
                                          f"{units} units (confidence: {analysis['confidence']:.2f})")
                    
                    # Small delay between instruments
                    await asyncio.sleep(1)
                
                # Wait before next analysis cycle
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)

    async def run(self):
        """Run the trader"""
        try:
            self.running = True
            logger.info("Trader started")
            
            # Initial balance check
            balance = await self.get_balance()
            if balance is None:
                logger.error("Failed to get initial balance. Check API credentials.")
                return
            
            logger.info(f"Initial balance: ${balance:.2f}")
            
            # Run trading loop
            await self.trading_loop()
            
        except Exception as e:
            logger.error(f"Error running trader: {e}")
            self.running = False
            raise

    def stop(self):
        """Stop the trader"""
        self.running = False
        logger.info("Trader stopped")

    async def get_status(self) -> Dict[str, Any]:
        """Get trader status"""
        return {
            'running': self.running,
            'last_balance': self.last_balance,
            'trade_count': self.trade_count,
            'instruments': self.instruments
        }