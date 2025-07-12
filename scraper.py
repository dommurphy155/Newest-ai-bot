#!/usr/bin/env python3
"""
Advanced Market Intelligence and Sentiment Analysis Engine
Scans market every 5 seconds, news every 10 seconds
Optimized for Maximum Profit Generation
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from collections import deque
import numpy as np
import feedparser
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import ccxt

logger = logging.getLogger(__name__)

class EnhancedNewsScraper:
    def __init__(self):
        self.session = None
        self.running = False
        self.last_news_scan = datetime.now()
        self.last_market_scan = datetime.now()
        
        # Enhanced headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Multiple news sources for maximum coverage
        self.news_sources = [
            {'name': 'Reuters Business', 'url': "https://feeds.feedburner.com/reuters/businessNews", 'type': 'rss', 'weight': 0.9, 'reliability': 0.95},
            {'name': 'Reuters UK Domestic', 'url': "https://feeds.feedburner.com/reuters/UKdomesticNews", 'type': 'rss', 'weight': 0.9, 'reliability': 0.95},
            {'name': 'Reuters World', 'url': "https://feeds.feedburner.com/reuters/worldNews", 'type': 'rss', 'weight': 0.9, 'reliability': 0.95},
            {'name': 'Reuters Politics', 'url': "https://feeds.feedburner.com/Reuters/PoliticsNews", 'type': 'rss', 'weight': 0.9, 'reliability': 0.95},
            {'name': 'CNBC', 'url': "https://www.cnbc.com/id/100003114/device/rss/rss.html", 'type': 'rss', 'weight': 0.75, 'reliability': 0.8},
            {'name': 'Financial Times', 'url': "https://www.ft.com/?format=rss", 'type': 'rss', 'weight': 0.85, 'reliability': 0.9},
            {'name': 'MarketWatch', 'url': "https://www.marketwatch.com/rss/topstories", 'type': 'rss', 'weight': 0.8, 'reliability': 0.85},
            {'name': 'Bloomberg ETF Podcast', 'url': "https://www.bloomberg.com/feed/podcast/etf-report.xml", 'type': 'rss', 'weight': 0.7, 'reliability': 0.8},
            {'name': 'Bloomberg Odds-On Podcast', 'url': "https://www.bloomberg.com/feed/podcast/odds-on.xml", 'type': 'rss', 'weight': 0.7, 'reliability': 0.8},
            {'name': 'Bloomberg What Goes Up Podcast', 'url': "https://www.bloomberg.com/feed/podcast/what-goes-up.xml", 'type': 'rss', 'weight': 0.7, 'reliability': 0.8},
            {'name': 'Investing.com', 'url': "https://www.investing.com/rss/news.rss", 'type': 'rss', 'weight': 0.8, 'reliability': 0.85}
        ]
        
        # Advanced sentiment analysis tools
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Enhanced market keywords for forex
        self.forex_keywords = {
            'currencies': {
                'USD': ['dollar', 'usd', 'greenback', 'buck'],
                'EUR': ['euro', 'eur', 'european'],
                'GBP': ['pound', 'sterling', 'gbp', 'british'],
                'JPY': ['yen', 'jpy', 'japanese'],
                'CHF': ['franc', 'chf', 'swiss'],
                'CAD': ['cad', 'canadian', 'loonie'],
                'AUD': ['aud', 'australian', 'aussie'],
                'NZD': ['nzd', 'kiwi', 'new zealand']
            },
            'central_banks': {
                'FED': ['fed', 'federal reserve', 'fomc', 'powell', 'yellen'],
                'ECB': ['ecb', 'european central bank', 'lagarde', 'draghi'],
                'BOE': ['bank of england', 'boe', 'bailey'],
                'BOJ': ['bank of japan', 'boj', 'kuroda'],
                'SNB': ['swiss national bank', 'snb'],
                'BOC': ['bank of canada', 'boc'],
                'RBA': ['reserve bank australia', 'rba']
            },
            'economic_indicators': [
                'gdp', 'inflation', 'cpi', 'ppi', 'employment', 'unemployment',
                'nfp', 'payroll', 'retail sales', 'manufacturing', 'pmi',
                'interest rate', 'bond yield', 'trade balance', 'current account'
            ],
            'market_events': [
                'brexit', 'trade war', 'election', 'crisis', 'summit',
                'meeting', 'decision', 'announcement', 'data release'
            ]
        }
        
        # Sentiment scoring weights
        self.sentiment_weights = {
            'very_positive': 1.0,
            'positive': 0.6,
            'neutral': 0.0,
            'negative': -0.6,
            'very_negative': -1.0
        }
        
        # Advanced sentiment keywords
        self.sentiment_keywords = {
            'very_positive': [
                'surge', 'soar', 'boom', 'explode', 'skyrocket', 'rally',
                'breakthrough', 'triumph', 'outperform', 'record high',
                'bullish', 'optimistic', 'confident', 'strong growth'
            ],
            'positive': [
                'rise', 'gain', 'grow', 'increase', 'advance', 'improve',
                'strengthen', 'recover', 'upbeat', 'positive', 'beat estimates'
            ],
            'neutral': [
                'stable', 'steady', 'unchanged', 'maintain', 'continue',
                'persist', 'hold', 'sideways', 'flat'
            ],
            'negative': [
                'fall', 'drop', 'decline', 'decrease', 'weaken', 'worry',
                'concern', 'bearish', 'pessimistic', 'disappointing', 'miss'
            ],
            'very_negative': [
                'crash', 'plunge', 'collapse', 'plummet', 'devastate',
                'disaster', 'crisis', 'panic', 'catastrophe', 'meltdown'
            ]
        }
        
        # Market data containers - Increased sizes for better performance
        self.sentiment_history = deque(maxlen=5000)  # Increased from 1000
        self.news_cache = deque(maxlen=2000)  # Increased from 500
        self.market_data_cache = {}
        
        # Performance tracking
        self.news_scans = 0
        self.market_scans = 0
        self.sentiment_scores = deque(maxlen=500)  # Increased from 100
        
        # Crypto exchange for additional market data
        self.crypto_exchange = None
        try:
            self.crypto_exchange = ccxt.binance()
        except Exception:
            logger.warning("Crypto exchange initialization failed")

    async def initialize(self):
        """Initialize the scraper"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers=self.headers
            )
            logger.info("✅ Market Intelligence System initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
            return False

    async def continuous_monitoring(self):
        """Continuous market and news monitoring"""
        try:
            self.running = True
            logger.info("🔥 Starting continuous market monitoring...")
            
            # Initialize session if not exists
            if not self.session:
                await self.initialize()
            
            while self.running:
                try:
                    current_time = datetime.now()
                    
                    # News scanning every 10 seconds
                    if (current_time - self.last_news_scan).total_seconds() >= 10:
                        asyncio.create_task(self.scan_news_sources())
                        self.last_news_scan = current_time
                    
                    # Market scanning every 5 seconds
                    if (current_time - self.last_market_scan).total_seconds() >= 5:
                        asyncio.create_task(self.scan_market_data())
                        self.last_market_scan = current_time
                    
                    # Brief pause to prevent overwhelming
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"Critical error in continuous monitoring: {e}")
        finally:
            if self.session and not self.session.closed:
                await self.session.close()

    async def scan_news_sources(self):
        """Scan all news sources for sentiment analysis"""
        try:
            self.news_scans += 1
            
            # Scan all sources concurrently
            tasks = [self.fetch_news_from_source(source) for source in self.news_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_articles = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
            
            if all_articles:
                # Analyze sentiment
                sentiment_score = await self.analyze_news_sentiment(all_articles)
                
                # Store in history
                self.sentiment_history.append({
                    'timestamp': datetime.now(),
                    'sentiment': sentiment_score,
                    'article_count': len(all_articles),
                    'sources_scanned': len(self.news_sources)
                })
                
                # Cache recent articles with larger buffer
                for article in all_articles[-200:]:  # Keep last 200 articles (increased from 50)
                    self.news_cache.append(article)
                
                logger.debug(f"📰 News scan complete: {len(all_articles)} articles, sentiment: {sentiment_score:.3f}")
                
        except Exception as e:
            logger.error(f"Error scanning news sources: {e}")

    async def fetch_news_from_source(self, source: Dict) -> List[Dict]:
        """Fetch news from a single source"""
        try:
            if source['type'] == 'rss':
                return await self.parse_rss_feed(source)
            else:
                return await self.fetch_json_news(source)
        except Exception as e:
            logger.error(f"Error fetching from {source['name']}: {e}")
            return []

    async def parse_rss_feed(self, source: Dict) -> List[Dict]:
        """Parse RSS feed for news articles"""
        try:
            async with self.session.get(source['url']) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:50]:  # Increased to 50 articles per source (from 20)
                        article = {
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'source': source['name'],
                            'weight': source['weight'],
                            'reliability': source['reliability'],
                            'timestamp': datetime.now()
                        }
                        articles.append(article)
                    
                    return articles
                    
        except Exception as e:
            logger.error(f"Error parsing RSS from {source['name']}: {e}")
            return []

    async def fetch_json_news(self, source: Dict) -> List[Dict]:
        """Fetch news from JSON API"""
        try:
            async with self.session.get(source['url']) as response:
                if response.status == 200:
                    data = await response.json()
                    # Process JSON data based on source format
                    return self.process_json_articles(data, source)
        except Exception as e:
            logger.error(f"Error fetching JSON from {source['name']}: {e}")
            return []

    def process_json_articles(self, data: Dict, source: Dict) -> List[Dict]:
        """Process JSON articles from various sources"""
        articles = []
        try:
            # Generic JSON processing - adapt based on actual API structure
            if 'articles' in data:
                for item in data['articles'][:50]:  # Increased to 50 articles (from 20)
                    article = {
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'published': item.get('publishedAt', ''),
                        'source': source['name'],
                        'weight': source['weight'],
                        'reliability': source['reliability'],
                        'timestamp': datetime.now()
                    }
                    articles.append(article)
        except Exception as e:
            logger.error(f"Error processing JSON articles: {e}")
        
        return articles

    async def analyze_news_sentiment(self, articles: List[Dict]) -> float:
        """Advanced sentiment analysis of news articles"""
        try:
            if not articles:
                return 0.5  # Neutral
            
            sentiment_scores = []
            forex_relevance_scores = []
            
            for article in articles:
                # Combine title and description
                text = f"{article.get('title', '')} {article.get('description', '')}"
                
                # Check forex relevance
                relevance = self.calculate_forex_relevance(text)
                forex_relevance_scores.append(relevance)
                
                if relevance > 0.3:  # Only analyze forex-relevant articles
                    # Multiple sentiment analysis methods
                    textblob_sentiment = TextBlob(text).sentiment.polarity
                    vader_sentiment = self.vader_analyzer.polarity_scores(text)['compound']
                    keyword_sentiment = self.calculate_keyword_sentiment(text)
                    
                    # Weighted combination
                    combined_sentiment = (
                        textblob_sentiment * 0.3 +
                        vader_sentiment * 0.4 +
                        keyword_sentiment * 0.3
                    )
                    
                    # Apply source weight and reliability
                    weighted_sentiment = combined_sentiment * article.get('weight', 1.0) * article.get('reliability', 1.0)
                    
                    sentiment_scores.append(weighted_sentiment * relevance)
            
            if sentiment_scores:
                # Calculate final sentiment with outlier handling
                final_sentiment = np.mean(sentiment_scores)
                
                # Normalize to 0-1 range (0.5 = neutral)
                normalized_sentiment = (final_sentiment + 1) / 2
                
                # Store for trending analysis
                self.sentiment_scores.append(normalized_sentiment)
                
                return normalized_sentiment
            else:
                return 0.5  # Neutral if no relevant articles
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.5

    def calculate_forex_relevance(self, text: str) -> float:
        """Calculate how relevant text is to forex trading"""
        try:
            text_lower = text.lower()
            relevance_score = 0.0
            
            # Check for currency mentions
            for currency, keywords in self.forex_keywords['currencies'].items():
                for keyword in keywords:
                    if keyword in text_lower:
                        relevance_score += 0.2
            
            # Check for central bank mentions
            for bank, keywords in self.forex_keywords['central_banks'].items():
                for keyword in keywords:
                    if keyword in text_lower:
                        relevance_score += 0.3
            
            # Check for economic indicators
            for indicator in self.forex_keywords['economic_indicators']:
                if indicator in text_lower:
                    relevance_score += 0.15
            
            # Check for market events
            for event in self.forex_keywords['market_events']:
                if event in text_lower:
                    relevance_score += 0.1
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating forex relevance: {e}")
            return 0.0

    def calculate_keyword_sentiment(self, text: str) -> float:
        """Calculate sentiment based on keyword analysis"""
        try:
            text_lower = text.lower()
            sentiment_score = 0.0
            keyword_count = 0
            
            for sentiment_type, keywords in self.sentiment_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        sentiment_score += self.sentiment_weights[sentiment_type]
                        keyword_count += 1
            
            if keyword_count > 0:
                return sentiment_score / keyword_count
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating keyword sentiment: {e}")
            return 0.0

    async def scan_market_data(self):
        """Scan market data for additional insights"""
        try:
            self.market_scans += 1
            
            # Get forex data
            forex_data = await self.get_forex_market_data()
            
            # Get crypto data if available
            crypto_data = await self.get_crypto_market_data()
            
            # Combine and analyze
            market_sentiment = self.analyze_market_sentiment(forex_data, crypto_data)
            
            # Store market data
            self.market_data_cache = {
                'timestamp': datetime.now(),
                'forex': forex_data,
                'crypto': crypto_data,
                'market_sentiment': market_sentiment
            }
            
            logger.debug(f"📊 Market scan complete: sentiment {market_sentiment:.3f}")
            
        except Exception as e:
            logger.error(f"Error scanning market data: {e}")

    async def get_forex_market_data(self) -> Dict:
        """Get real-time forex market data"""
        try:
            # Get major currency pairs data
            symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X']
            forex_data = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d', interval='1m')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        change = hist['Close'].iloc[-1] - hist['Close'].iloc[0]
                        change_pct = (change / hist['Close'].iloc[0]) * 100
                        
                        forex_data[symbol] = {
                            'price': current_price,
                            'change': change,
                            'change_pct': change_pct,
                            'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                        }
                except Exception:
                    continue
            
            return forex_data
            
        except Exception as e:
            logger.error(f"Error getting forex data: {e}")
            return {}

    async def get_crypto_market_data(self) -> Dict:
        """Get cryptocurrency market data for additional sentiment"""
        try:
            if not self.crypto_exchange:
                return {}
            
            # Get major crypto pairs
            crypto_data = {}
            symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT']
            
            for symbol in symbols:
                try:
                    ticker = self.crypto_exchange.fetch_ticker(symbol)
                    crypto_data[symbol] = {
                        'price': ticker['last'],
                        'change': ticker['change'],
                        'change_pct': ticker['percentage'],
                        'volume': ticker['quoteVolume']
                    }
                except Exception:
                    continue
            
            return crypto_data
            
        except Exception as e:
            logger.error(f"Error getting crypto data: {e}")
            return {}

    def analyze_market_sentiment(self, forex_data: Dict, crypto_data: Dict) -> float:
        """Analyze overall market sentiment from price data"""
        try:
            sentiment_factors = []
            
            # Analyze forex movements
            for symbol, data in forex_data.items():
                change_pct = data.get('change_pct', 0)
                if abs(change_pct) > 0.1:  # Significant movement
                    sentiment_factors.append(change_pct / 100)  # Normalize
            
            # Analyze crypto movements (as risk sentiment indicator)
            for symbol, data in crypto_data.items():
                change_pct = data.get('change_pct', 0)
                if abs(change_pct) > 1:  # Crypto is more volatile
                    sentiment_factors.append(change_pct / 500)  # Heavily normalized
            
            if sentiment_factors:
                avg_sentiment = np.mean(sentiment_factors)
                # Convert to 0-1 range (0.5 = neutral)
                return max(0, min(1, avg_sentiment + 0.5))
            else:
                return 0.5  # Neutral
                
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {e}")
            return 0.5

    async def get_sentiment(self) -> float:
        """Get current sentiment score"""
        try:
            if self.sentiment_history:
                # Get weighted average of recent sentiment
                recent_sentiments = list(self.sentiment_history)[-10:]  # Last 10 readings
                
                weights = []
                values = []
                
                for i, entry in enumerate(recent_sentiments):
                    # More weight to recent entries
                    weight = (i + 1) / len(recent_sentiments)
                    weights.append(weight)
                    values.append(entry['sentiment'])
                
                weighted_sentiment = np.average(values, weights=weights)
                return weighted_sentiment
            else:
                return 0.5  # Neutral default
                
        except Exception as e:
            logger.error(f"Error getting sentiment: {e}")
            return 0.5

    async def get_sentiment_trend(self) -> str:
        """Get sentiment trend direction"""
        try:
            if len(self.sentiment_scores) >= 5:
                recent_scores = list(self.sentiment_scores)[-5:]
                trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
                
                if trend > 0.02:
                    return 'IMPROVING'
                elif trend < -0.02:
                    return 'DECLINING'
                else:
                    return 'STABLE'
            else:
                return 'INSUFFICIENT_DATA'
                
        except Exception as e:
            logger.error(f"Error calculating sentiment trend: {e}")
            return 'UNKNOWN'

    def get_stats(self) -> Dict[str, Any]:
        """Get scraper performance statistics"""
        return {
            'running': self.running,
            'news_scans': self.news_scans,
            'market_scans': self.market_scans,
            'sentiment_history_length': len(self.sentiment_history),
            'news_cache_length': len(self.news_cache),
            'current_sentiment': self.get_sentiment() if asyncio.iscoroutinefunction(self.get_sentiment) else 0.5,
            'sources_configured': len(self.news_sources)
        }

    def stop(self):
        """Stop the scraper"""
        self.running = False
        logger.info("🛑 Market Intelligence System stopped")

# Maintain backward compatibility
# EnhancedNewsScraper = AdvancedMarketIntelligence