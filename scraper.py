#!/usr/bin/env python3
"""
News Scraper for AI Trading Bot
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup not installed. HTML parsing will be limited.")

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # News sources (using free/public APIs and RSS feeds)
        self.sources = [
            {
                'name': 'ForexFactory',
                'url': 'https://www.forexfactory.com/rss',
                'type': 'rss'
            },
            {
                'name': 'Investing.com',
                'url': 'https://www.investing.com/rss/news_25.rss',
                'type': 'rss'
            },
            {
                'name': 'FXStreet',
                'url': 'https://www.fxstreet.com/news/rss',
                'type': 'rss'
            }
        ]
        
        # Sentiment keywords
        self.positive_words = [
            'bullish', 'rally', 'surge', 'gain', 'rise', 'strong', 'growth',
            'positive', 'optimistic', 'boost', 'increase', 'upward', 'recover'
        ]
        
        self.negative_words = [
            'bearish', 'decline', 'fall', 'drop', 'weak', 'negative', 'crash',
            'pessimistic', 'decrease', 'downward', 'plunge', 'concern', 'fear'
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from URL with error handling"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {url}: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_rss(self, content: str) -> List[Dict[str, Any]]:
        """Parse RSS feed content"""
        articles = []
        
        if not BeautifulSoup:
            logger.warning("BeautifulSoup not available for RSS parsing")
            return articles
        
        try:
            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                try:
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    article = {
                        'title': title.get_text().strip() if title else '',
                        'description': description.get_text().strip() if description else '',
                        'published': pub_date.get_text().strip() if pub_date else '',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if article['title'] or article['description']:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing RSS content: {e}")
            
        return articles

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (simple keyword-based approach)"""
        if not text:
            return 0.5
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.5
        
        # Normalize sentiment score
        positive_score = positive_count / max(total_words, 1)
        negative_score = negative_count / max(total_words, 1)
        
        # Calculate sentiment (0 = very negative, 1 = very positive, 0.5 = neutral)
        if positive_score + negative_score == 0:
            return 0.5
        
        sentiment = positive_score / (positive_score + negative_score)
        
        # Adjust for magnitude
        magnitude = min((positive_score + negative_score) * 10, 1.0)
        sentiment = 0.5 + (sentiment - 0.5) * magnitude
        
        return max(0.0, min(1.0, sentiment))

    async def scrape_news(self) -> List[Dict[str, Any]]:
        """Scrape news from all sources"""
        all_articles = []
        
        try:
            tasks = []
            for source in self.sources:
                task = self.fetch_url(source['url'])
                tasks.append((source, task))
            
            # Execute all fetches concurrently
            for source, task in tasks:
                try:
                    content = await task
                    if content:
                        if source['type'] == 'rss':
                            articles = self.parse_rss(content)
                            for article in articles:
                                article['source'] = source['name']
                                article['sentiment'] = self.analyze_sentiment(
                                    f"{article['title']} {article['description']}"
                                )
                            all_articles.extend(articles)
                        
                except Exception as e:
                    logger.error(f"Error processing {source['name']}: {e}")
                    continue
            
            logger.info(f"Scraped {len(all_articles)} articles from {len(self.sources)} sources")
            return all_articles
            
        except Exception as e:
            logger.error(f"Error in scrape_news: {e}")
            return []

    async def get_sentiment(self) -> float:
        """Get overall market sentiment from news"""
        try:
            articles = await self.scrape_news()
            
            if not articles:
                logger.warning("No articles found, returning neutral sentiment")
                return 0.5
            
            # Calculate weighted average sentiment
            total_sentiment = 0.0
            total_weight = 0.0
            
            for article in articles:
                # Weight more recent articles higher
                weight = 1.0  # You can implement time-based weighting here
                
                sentiment = article.get('sentiment', 0.5)
                total_sentiment += sentiment * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.5
            
            overall_sentiment = total_sentiment / total_weight
            logger.info(f"Overall market sentiment: {overall_sentiment:.3f} (from {len(articles)} articles)")
            
            return overall_sentiment
            
        except Exception as e:
            logger.error(f"Error getting sentiment: {e}")
            return 0.5

    async def get_latest_headlines(self, limit: int = 10) -> List[str]:
        """Get latest headlines for reporting"""
        try:
            articles = await self.scrape_news()
            headlines = []
            
            for article in articles[:limit]:
                if article.get('title'):
                    headlines.append(f"• {article['title']}")
            
            return headlines
            
        except Exception as e:
            logger.error(f"Error getting headlines: {e}")
            return []

# Legacy functions for backward compatibility
async def fetch_html(session, url):
    """Legacy function - use NewsScraper instead"""
    scraper = NewsScraper()
    scraper.session = session
    return await scraper.fetch_url(url)

async def scrape_news():
    """Legacy function - use NewsScraper instead"""
    async with NewsScraper() as scraper:
        articles = await scraper.scrape_news()
        return [article.get('title', 'Sample headline') for article in articles]