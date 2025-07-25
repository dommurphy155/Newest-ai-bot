#!/usr/bin/env python3
"""
Database Management for AI Trading Bot
"""

import os
import aiosqlite
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Trade data structure"""
    id: Optional[int] = None
    instrument: str = ""
    side: str = ""
    units: int = 0
    price: float = 0.0
    timestamp: datetime = None
    pnl: float = 0.0
    commission: float = 0.0
    confidence: float = 0.0
    sentiment: float = 0.5
    status: str = "pending"
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class Position:
    """Position data structure"""
    instrument: str
    units: int
    avg_price: float
    unrealized_pnl: float
    timestamp: datetime

class Database:
    """Async database manager for trading bot"""
    def __init__(self, db_path: str = "data/trading_bot.db"):
        self.db_path = db_path
        self._ensure_directory()

    def _ensure_directory(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def initialize(self):
        """Initialize database and create tables if missing."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Memory optimization for better performance - using more memory when available
                await db.execute("PRAGMA cache_size = -8192")  # 8MB cache (increased from 2MB)
                await db.execute("PRAGMA temp_store = MEMORY")
                await db.execute("PRAGMA mmap_size = 268435456")  # 256MB mmap (increased from 64MB)
                await db.execute("PRAGMA journal_mode = WAL")
                await db.execute("PRAGMA synchronous = NORMAL")
                await db.execute("PRAGMA page_size = 4096")
                await db.execute("PRAGMA wal_autocheckpoint = 1000")  # Checkpoint every 1000 pages
                await db.execute("PRAGMA optimize")  # Optimize database performance
                
                await self._create_tables(db)
                await db.commit()
            logger.info("Database initialized successfully with enhanced memory settings")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def _create_tables(self, db):
        """Create all necessary tables and indexes."""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL,
                side TEXT NOT NULL,
                units INTEGER NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                pnl REAL DEFAULT 0.0,
                commission REAL DEFAULT 0.0,
                confidence REAL DEFAULT 0.5,
                sentiment REAL DEFAULT 0.5,
                status TEXT DEFAULT 'pending',
                metadata TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL,
                units INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0.0,
                timestamp DATETIME NOT NULL,
                status TEXT DEFAULT 'open'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                trade_count INTEGER DEFAULT 0,
                daily_pnl REAL DEFAULT 0.0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS market_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL NOT NULL,
                sentiment REAL NOT NULL,
                price_data TEXT,
                indicators TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                sentiment REAL NOT NULL,
                article_count INTEGER DEFAULT 0,
                headlines TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0
            )
        """)
        # Indexes for performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trades_instrument ON trades(instrument)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_positions_instrument ON positions(instrument)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_balance_timestamp ON balance_history(timestamp)")

    async def save_trade(self, trade: Trade) -> int:
        """Save a trade to database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO trades (instrument, side, units, price, timestamp, 
                                      pnl, commission, confidence, sentiment, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade.instrument, trade.side, trade.units, trade.price,
                    trade.timestamp, trade.pnl, trade.commission,
                    trade.confidence, trade.sentiment, trade.status
                ))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return -1

    async def get_trades(self, instrument: str = None, 
                        start_date: datetime = None, 
                        end_date: datetime = None,
                        limit: int = 100) -> List[Trade]:
        """Get trades from database."""
        try:
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            if instrument:
                query += " AND instrument = ?"
                params.append(instrument)
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                
                trades = []
                for row in rows:
                    trade = Trade(
                        id=row[0],
                        instrument=row[1],
                        side=row[2],
                        units=row[3],
                        price=row[4],
                        timestamp=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        pnl=row[6],
                        commission=row[7],
                        confidence=row[8],
                        sentiment=row[9],
                        status=row[10]
                    )
                    trades.append(trade)
                
                return trades
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []

    async def save_balance(self, balance: float, trade_count: int = 0, daily_pnl: float = 0.0):
        """Save account balance."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO balance_history (balance, timestamp, trade_count, daily_pnl)
                    VALUES (?, ?, ?, ?)
                    """,
                    (balance, datetime.now(), trade_count, daily_pnl)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Error saving balance: {e}")

    async def get_latest_balance(self) -> Optional[float]:
        """Get latest balance from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT balance FROM balance_history 
                    ORDER BY timestamp DESC LIMIT 1
                    """
                )
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting latest balance: {e}")
            return None

    async def save_market_analysis(self, instrument: str, signal: str, confidence: float, sentiment: float, price_data: Dict = None, indicators: Dict = None):
        """Save market analysis data."""
        import json
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO market_analysis (instrument, timestamp, signal, confidence, sentiment, price_data, indicators)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (instrument, datetime.now(), signal, confidence, sentiment, json.dumps(price_data) if price_data else None, json.dumps(indicators) if indicators else None)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Error saving market analysis: {e}")

    async def save_news_sentiment(self, sentiment: float, article_count: int, headlines: List[str]):
        """Save news sentiment data."""
        import json
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO news_sentiment (timestamp, sentiment, article_count, headlines)
                    VALUES (?, ?, ?, ?)
                    """,
                    (datetime.now(), sentiment, article_count, json.dumps(headlines))
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Error saving news sentiment: {e}")

    async def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate and save performance metrics."""
        import statistics
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT COUNT(*) as total_trades,
                           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                           SUM(pnl) as total_pnl,
                           AVG(pnl) as avg_pnl,
                           MIN(pnl) as min_pnl,
                           MAX(pnl) as max_pnl
                    FROM trades
                    WHERE status = 'completed'
                    """
                )
                stats = await cursor.fetchone()
                if not stats or stats[0] == 0:
                    return {}
                total_trades, winning_trades, total_pnl, avg_pnl, min_pnl, max_pnl = stats
                win_rate = winning_trades / total_trades if total_trades > 0 else 0
                # Calculate max drawdown
                cursor = await db.execute(
                    """
                    SELECT pnl FROM trades WHERE status = 'completed' ORDER BY timestamp ASC
                    """
                )
                pnls = [row[0] for row in await cursor.fetchall()]
                max_drawdown, running_pnl, peak = 0.0, 0.0, 0.0
                for pnl in pnls:
                    running_pnl += pnl
                    if running_pnl > peak:
                        peak = running_pnl
                    drawdown = peak - running_pnl
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                sharpe_ratio = (avg_pnl / statistics.stdev(pnls)) if len(pnls) > 1 and statistics.stdev(pnls) > 0 else 0
                metrics = {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'total_pnl': total_pnl,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'win_rate': win_rate,
                    'avg_pnl': avg_pnl,
                    'min_pnl': min_pnl,
                    'max_pnl': max_pnl
                }
                await db.execute(
                    """
                    INSERT INTO performance_metrics (timestamp, total_trades, winning_trades, total_pnl, max_drawdown, sharpe_ratio, win_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (datetime.now(), total_trades, winning_trades, total_pnl, max_drawdown, sharpe_ratio, win_rate)
                )
                await db.commit()
                return metrics
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

    async def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily trading statistics."""
        if date is None:
            date = datetime.now().date()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT COUNT(*) as trades, SUM(pnl) as total_pnl, AVG(pnl) as avg_pnl, SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades
                    FROM trades WHERE DATE(timestamp) = ?
                    """,
                    (date,)
                )
                row = await cursor.fetchone()
                if row:
                    trades, total_pnl, avg_pnl, winning_trades = row
                    win_rate = winning_trades / trades if trades > 0 else 0
                    return {
                        'date': date.isoformat(),
                        'trades': trades,
                        'total_pnl': total_pnl or 0,
                        'avg_pnl': avg_pnl or 0,
                        'winning_trades': winning_trades or 0,
                        'win_rate': win_rate
                    }
                return {}
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to save space."""
        from datetime import timedelta
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM market_analysis WHERE timestamp < ?", (cutoff_date,))
                await db.execute("DELETE FROM news_sentiment WHERE timestamp < ?", (cutoff_date,))
                await db.commit()
                logger.info(f"Cleaned up data older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    async def execute(self, query: str, params: tuple = None):
        """Execute arbitrary SQL query - used for cleanup operations"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if params:
                    await db.execute(query, params)
                else:
                    await db.execute(query)
                await db.commit()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
