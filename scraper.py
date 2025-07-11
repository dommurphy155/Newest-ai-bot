#!/usr/bin/env python3
"""
Enhanced News Scraper with Advanced Sentiment Analysis
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import asyncio
import aiohttp
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)

class EnhancedNewsScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Enhanced news sources with API endpoints
        self.sources = [
            {
                'name': 'MarketWatch',
                'url': 'https://www.marketwatch.com/rss/realtimeheadlines',
                'type': 'rss',
                'weight': 0.8
            },
            {
                'name': 'Yahoo Finance',
                'url': 'https://finance.yahoo.com/rss/headline',
                'type': 'rss',
                'weight': 0.7
            },
            {
                'name': 'Reuters',
                'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
                'type': 'json',
                'weight': 0.9
            },
            {
                'name': 'Bloomberg',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'type': 'rss',
                'weight': 0.9
            },
            {
                'name': 'Financial Times',
                'url': 'https://www.ft.com/rss/home',
                'type': 'rss',
                'weight': 0.8
            }
        ]
        
        # Advanced sentiment lexicon
        self.sentiment_lexicon = {
            'very_positive': ['surge', 'soar', 'boom', 'explode', 'skyrocket', 'rally', 'breakthrough', 'triumph'],
            'positive': ['rise', 'gain', 'grow', 'increase', 'advance', 'improve', 'strengthen', 'optimistic', 'bullish'],
            'neutral': ['stable', 'steady', 'unchanged', 'maintain', 'continue', 'persist'],
            'negative': ['fall', 'drop', 'decline', 'decrease', 'weaken', 'worry', 'concern', 'bearish', 'pessimistic'],
            'very_negative': ['crash', 'plunge', 'collapse', 'plummet', 'devastate', 'disaster', 'crisis', 'panic']
        }
        
        # Market-specific keywords
        self.market_keywords = {
            'forex': ['dollar', 'euro', 'pound', 'yen', 'currency', 'exchange', 'forex', 'fx'],
            'central_bank': ['fed', 'federal reserve', 'ecb', 'bank of england', 'boj', 'central bank', 'monetary policy', 'interest rate'],
            'economic': ['gdp', 'inflation', 'employment', 'unemployment', 'trade', 'economic', 'economy'],
            'geopolitical': ['trade war', 'brexit', 'election', 'political', 'war', 'conflict', 'sanctions']
        }
        
        # Sentiment history for trending analysis
        self.sentiment_history = deque(maxlen=100)
        self.