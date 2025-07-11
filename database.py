#!/usr/bin/env python3
"""
🚀 ULTRA-OPTIMIZED DATABASE MANAGEMENT v3.0
High-performance async database with advanced features
Compatible with Python 3.8+ and Ubuntu 20.04
"""

import os
import aiosqlite
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import asyncio
from collections import deque
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Enhanced trade data structure"""
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
    strategy: str = "unknown"
    risk_level: str = "LOW"
    market_regime: str = "NORMAL"
    analysis_data: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.analysis_data is None:
            self.analysis_data = {}

@dataclass
class Position:
    """Enhanced position data structure"""
    instrument: str
    units: int
    avg_price: float
    unrealized_pnl: float
    timestamp: datetime
    side: str = "LONG"
    strategy: str = "unknown"
    risk_level: str = "LOW"

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    total_trades: int = 0
    winning_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration: float = 0.0
    max_consecutive_losses: int = 0
    current_consecutive_losses: int = 0
    daily_pnl: float = 0.0
    hourly_pnl: float = 0.0
    peak_balance: float = 0.0
    current_balance: float = 0.0

class UltraOptimizedDatabase:
    """Ultra-optimized async database manager for trading bot"""
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        self.db_path = db_path
        self._ensure_directory()
        self.connection_pool = deque(maxlen=5)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cleanup = datetime.now()

    def _ensure_directory(self):
        """Ensure required directories exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs("data/backups", exist_ok=True)
        os.makedirs("data/exports", exist_ok=True)

    async def initialize(self):
        """Initialize database and create tables if missing."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await self._create_indexes(db)
                await self._create_triggers(db)
                await db.commit()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def _create_tables(self, db):
        """Create all necessary tables with enhanced schema"""
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
                strategy TEXT DEFAULT 'unknown',
                risk_level TEXT DEFAULT 'LOW',
                market_regime TEXT DEFAULT 'NORMAL',
                analysis_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                side TEXT DEFAULT 'LONG',
                strategy TEXT DEFAULT 'unknown',
                risk_level TEXT DEFAULT 'LOW',
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                trade_count INTEGER DEFAULT 0,
                daily_pnl REAL DEFAULT 0.0,
                hourly_pnl REAL DEFAULT 0.0,
                peak_balance REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                strategy TEXT DEFAULT 'unknown',
                risk_level TEXT DEFAULT 'LOW',
                price_data TEXT,
                indicators TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                sentiment REAL NOT NULL,
                article_count INTEGER DEFAULT 0,
                headlines TEXT,
                source TEXT DEFAULT 'unknown',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                win_rate REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                avg_trade_duration REAL DEFAULT 0.0,
                max_consecutive_losses INTEGER DEFAULT 0,
                current_consecutive_losses INTEGER DEFAULT 0,
                daily_pnl REAL DEFAULT 0.0,
                hourly_pnl REAL DEFAULT 0.0,
                peak_balance REAL DEFAULT 0.0,
                current_balance REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                pnl REAL DEFAULT 0.0,
                accuracy REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                memory_usage REAL DEFAULT 0.0,
                cpu_usage REAL DEFAULT 0.0,
                disk_usage REAL DEFAULT 0.0,
                uptime_seconds REAL DEFAULT 0.0,
                message_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    async def _create_indexes(self, db):
        """Create performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_trades_instrument ON trades(instrument)",
            "CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy)",
            "CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)",
            "CREATE INDEX IF NOT EXISTS idx_positions_instrument ON positions(instrument)",
            "CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)",
            "CREATE INDEX IF NOT EXISTS idx_balance_timestamp ON balance_history(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_market_analysis_instrument ON market_analysis(instrument)",
            "CREATE INDEX IF NOT EXISTS idx_market_analysis_timestamp ON market_analysis(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_strategy_performance_strategy ON strategy_performance(strategy)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)"
        ]
        
        for index in indexes:
            await db.execute(index)

    async def _create_triggers(self, db):
        """Create database triggers for automatic updates"""
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_trades_timestamp
            AFTER UPDATE ON trades
            BEGIN
                UPDATE trades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """)
        
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_positions_timestamp
            AFTER UPDATE ON positions
            BEGIN
                UPDATE positions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """)

    async def save_trade(self, trade: Trade) -> int:
        """Save a trade to database with enhanced features"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO trades (instrument, side, units, price, timestamp, 
                                      pnl, commission, confidence, sentiment, status,
                                      strategy, risk_level, market_regime, analysis_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade.instrument, trade.side, trade.units, trade.price,
                    trade.timestamp, trade.pnl, trade.commission,
                    trade.confidence, trade.sentiment, trade.status,
                    trade.strategy, trade.risk_level, trade.market_regime,
                    json.dumps(trade.analysis_data)
                ))
                await db.commit()
                trade_id = cursor.lastrowid
                
                # Update cache
                cache_key = f"trade_{trade_id}"
                self.cache[cache_key] = asdict(trade)
                
                logger.info(f"✅ Trade saved: {trade.instrument} {trade.side} {trade.units}")
                return trade_id
        except Exception as e:
            logger.error(f"❌ Error saving trade: {e}")
            return -1

    async def get_trades(self, instrument: str = None, 
                        start_date: datetime = None, 
                        end_date: datetime = None,
                        strategy: str = None,
                        status: str = None,
                        limit: int = 100) -> List[Trade]:
        """Get trades from database with enhanced filtering"""
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
            if strategy:
                query += " AND strategy = ?"
                params.append(strategy)
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                
                trades = []
                for row in rows:
                    trade = Trade(
                        id=row['id'],
                        instrument=row['instrument'],
                        side=row['side'],
                        units=row['units'],
                        price=row['price'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        pnl=row['pnl'],
                        commission=row['commission'],
                        confidence=row['confidence'],
                        sentiment=row['sentiment'],
                        status=row['status'],
                        strategy=row['strategy'],
                        risk_level=row['risk_level'],
                        market_regime=row['market_regime'],
                        analysis_data=json.loads(row['analysis_data']) if row['analysis_data'] else {}
                    )
                    trades.append(trade)
                
                return trades
        except Exception as e:
            logger.error(f"❌ Error getting trades: {e}")
            return []

    async def save_balance(self, balance: float, trade_count: int = 0, 
                          daily_pnl: float = 0.0, hourly_pnl: float = 0.0,
                          peak_balance: float = 0.0, max_drawdown: float = 0.0):
        """Save account balance with enhanced metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO balance_history (balance, timestamp, trade_count, daily_pnl, 
                                               hourly_pnl, peak_balance, max_drawdown)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (balance, datetime.now(), trade_count, daily_pnl, 
                     hourly_pnl, peak_balance, max_drawdown)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving balance: {e}")

    async def get_latest_balance(self) -> Optional[float]:
        """Get latest balance from database with caching"""
        try:
            cache_key = "latest_balance"
            if cache_key in self.cache:
                cache_data = self.cache[cache_key]
                if (datetime.now() - cache_data['timestamp']).seconds < self.cache_ttl:
                    return cache_data['balance']
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT balance FROM balance_history 
                    ORDER BY timestamp DESC LIMIT 1
                    """
                )
                row = await cursor.fetchone()
                
                if row:
                    balance = row[0]
                    self.cache[cache_key] = {
                        'balance': balance,
                        'timestamp': datetime.now()
                    }
                    return balance
                return None
        except Exception as e:
            logger.error(f"❌ Error getting latest balance: {e}")
            return None

    async def save_market_analysis(self, instrument: str, signal: str, confidence: float, 
                                 sentiment: float, strategy: str = "unknown", 
                                 risk_level: str = "LOW", price_data: Dict = None, 
                                 indicators: Dict = None):
        """Save market analysis with enhanced data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO market_analysis (instrument, timestamp, signal, confidence, 
                                               sentiment, strategy, risk_level, price_data, indicators)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (instrument, datetime.now(), signal, confidence, sentiment,
                     strategy, risk_level, json.dumps(price_data) if price_data else None,
                     json.dumps(indicators) if indicators else None)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving market analysis: {e}")

    async def save_news_sentiment(self, sentiment: float, article_count: int, 
                                headlines: List[str], source: str = "unknown"):
        """Save news sentiment with source tracking"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO news_sentiment (timestamp, sentiment, article_count, headlines, source)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (datetime.now(), sentiment, article_count, 
                     json.dumps(headlines), source)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving news sentiment: {e}")

    async def save_performance_metrics(self, metrics: PerformanceMetrics):
        """Save comprehensive performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO performance_metrics (timestamp, total_trades, winning_trades,
                                                   total_pnl, max_drawdown, sharpe_ratio, win_rate,
                                                   profit_factor, avg_trade_duration, max_consecutive_losses,
                                                   current_consecutive_losses, daily_pnl, hourly_pnl,
                                                   peak_balance, current_balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (metrics.timestamp, metrics.total_trades, metrics.winning_trades,
                     metrics.total_pnl, metrics.max_drawdown, metrics.sharpe_ratio, metrics.win_rate,
                     metrics.profit_factor, metrics.avg_trade_duration, metrics.max_consecutive_losses,
                     metrics.current_consecutive_losses, metrics.daily_pnl, metrics.hourly_pnl,
                     metrics.peak_balance, metrics.current_balance)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving performance metrics: {e}")

    async def save_strategy_performance(self, strategy: str, wins: int, losses: int, 
                                      pnl: float, accuracy: float):
        """Save strategy performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO strategy_performance (strategy, timestamp, wins, losses, pnl, accuracy)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (strategy, datetime.now(), wins, losses, pnl, accuracy)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving strategy performance: {e}")

    async def save_system_metrics(self, memory_usage: float, cpu_usage: float, 
                                disk_usage: float, uptime_seconds: float,
                                message_count: int, error_count: int):
        """Save system metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO system_metrics (timestamp, memory_usage, cpu_usage, disk_usage,
                                              uptime_seconds, message_count, error_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (datetime.now(), memory_usage, cpu_usage, disk_usage,
                     uptime_seconds, message_count, error_count)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error saving system metrics: {e}")

    async def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get basic trade statistics
                cursor = await db.execute("""
                    SELECT COUNT(*) as total_trades,
                           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                           SUM(pnl) as total_pnl,
                           AVG(pnl) as avg_pnl,
                           MAX(pnl) as best_trade,
                           MIN(pnl) as worst_trade
                    FROM trades
                    WHERE status = 'closed'
                """)
                trade_stats = await cursor.fetchone()
                
                # Calculate win rate
                total_trades = trade_stats[0] or 0
                winning_trades = trade_stats[1] or 0
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                # Calculate profit factor
                total_pnl = trade_stats[2] or 0
                avg_pnl = trade_stats[3] or 0
                
                # Get drawdown information
                cursor = await db.execute("""
                    SELECT peak_balance, max_drawdown FROM balance_history 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                balance_stats = await cursor.fetchone()
                peak_balance = balance_stats[0] if balance_stats else 0
                max_drawdown = balance_stats[1] if balance_stats else 0
                
                # Calculate Sharpe ratio (simplified)
                cursor = await db.execute("""
                    SELECT AVG(pnl) as avg_pnl, STDDEV(pnl) as std_pnl
                    FROM trades WHERE status = 'closed'
                """)
                risk_stats = await cursor.fetchone()
                sharpe_ratio = 0
                if risk_stats and risk_stats[1] and risk_stats[1] > 0:
                    sharpe_ratio = risk_stats[0] / risk_stats[1]
                
                return {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'win_rate': win_rate,
                    'total_pnl': total_pnl,
                    'avg_pnl': avg_pnl,
                    'best_trade': trade_stats[4] or 0,
                    'worst_trade': trade_stats[5] or 0,
                    'peak_balance': peak_balance,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'profit_factor': abs(total_pnl / max_drawdown) if max_drawdown > 0 else 0
                }
        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {e}")
            return {}

    async def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily trading statistics"""
        try:
            if date is None:
                date = datetime.now()
            
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT COUNT(*) as trades,
                           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                           SUM(pnl) as pnl,
                           AVG(pnl) as avg_pnl
                    FROM trades
                    WHERE timestamp >= ? AND timestamp < ?
                """, (start_date, end_date))
                
                stats = await cursor.fetchone()
                
                return {
                    'date': date.strftime('%Y-%m-%d'),
                    'trades': stats[0] or 0,
                    'wins': stats[1] or 0,
                    'pnl': stats[2] or 0,
                    'avg_pnl': stats[3] or 0,
                    'win_rate': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
                }
        except Exception as e:
            logger.error(f"❌ Error getting daily stats: {e}")
            return {}

    async def get_strategy_performance(self, days: int = 30) -> Dict[str, Dict]:
        """Get strategy performance over specified period"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT strategy,
                           COUNT(*) as trades,
                           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                           SUM(pnl) as pnl,
                           AVG(pnl) as avg_pnl
                    FROM trades
                    WHERE timestamp >= ?
                    GROUP BY strategy
                    ORDER BY pnl DESC
                """, (start_date,))
                
                rows = await cursor.fetchall()
                
                strategy_performance = {}
                for row in rows:
                    strategy = row[0]
                    trades = row[1]
                    wins = row[2]
                    pnl = row[3]
                    avg_pnl = row[4]
                    
                    strategy_performance[strategy] = {
                        'trades': trades,
                        'wins': wins,
                        'losses': trades - wins,
                        'pnl': pnl,
                        'avg_pnl': avg_pnl,
                        'win_rate': (wins / trades * 100) if trades > 0 else 0
                    }
                
                return strategy_performance
        except Exception as e:
            logger.error(f"❌ Error getting strategy performance: {e}")
            return {}

    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to maintain performance"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Clean up old trades
                await db.execute("DELETE FROM trades WHERE timestamp < ?", (cutoff_date,))
                
                # Clean up old balance history
                await db.execute("DELETE FROM balance_history WHERE timestamp < ?", (cutoff_date,))
                
                # Clean up old market analysis
                await db.execute("DELETE FROM market_analysis WHERE timestamp < ?", (cutoff_date,))
                
                # Clean up old news sentiment
                await db.execute("DELETE FROM news_sentiment WHERE timestamp < ?", (cutoff_date,))
                
                # Clean up old system metrics
                await db.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_date,))
                
                await db.commit()
                
                # Vacuum database to reclaim space
                await db.execute("VACUUM")
                
                logger.info(f"✅ Cleaned up data older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {e}")

    async def create_backup(self) -> str:
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/backups/trading_bot_backup_{timestamp}.db"
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"✅ Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return ""

    async def export_data(self, format: str = "json") -> str:
        """Export data in specified format"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = f"data/exports/trading_data_{timestamp}.{format}"
            
            if format == "json":
                await self._export_to_json(export_path)
            elif format == "csv":
                await self._export_to_csv(export_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"✅ Data exported to: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"❌ Error exporting data: {e}")
            return ""

    async def _export_to_json(self, export_path: str):
        """Export data to JSON format"""
        try:
            # Get all trades
            trades = await self.get_trades(limit=10000)
            
            # Get performance metrics
            metrics = await self.calculate_performance_metrics()
            
            # Get strategy performance
            strategy_perf = await self.get_strategy_performance()
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'trades': [asdict(trade) for trade in trades],
                'performance_metrics': metrics,
                'strategy_performance': strategy_perf
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error exporting to JSON: {e}")

    async def _export_to_csv(self, export_path: str):
        """Export data to CSV format"""
        try:
            import csv
            
            trades = await self.get_trades(limit=10000)
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['id', 'instrument', 'side', 'units', 'price', 
                               'timestamp', 'pnl', 'commission', 'confidence', 
                               'sentiment', 'status', 'strategy', 'risk_level'])
                
                # Write data
                for trade in trades:
                    writer.writerow([
                        trade.id, trade.instrument, trade.side, trade.units,
                        trade.price, trade.timestamp, trade.pnl, trade.commission,
                        trade.confidence, trade.sentiment, trade.status,
                        trade.strategy, trade.risk_level
                    ])
        except Exception as e:
            logger.error(f"❌ Error exporting to CSV: {e}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Get table sizes
                tables = ['trades', 'positions', 'balance_history', 'market_analysis', 
                         'news_sentiment', 'performance_metrics', 'strategy_performance', 
                         'system_metrics']
                
                for table in tables:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    stats[f"{table}_count"] = count[0] if count else 0
                
                # Get database size
                cursor = await db.execute("PRAGMA page_count")
                page_count = await cursor.fetchone()
                cursor = await db.execute("PRAGMA page_size")
                page_size = await cursor.fetchone()
                
                db_size = (page_count[0] * page_size[0]) / (1024 * 1024)  # MB
                stats['database_size_mb'] = db_size
                
                return stats
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {}

    async def optimize_database(self):
        """Optimize database performance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Analyze tables for better query planning
                await db.execute("ANALYZE")
                
                # Update statistics
                await db.execute("PRAGMA optimize")
                
                # Clean up cache
                self.cache.clear()
                
                logger.info("✅ Database optimized")
        except Exception as e:
            logger.error(f"❌ Error optimizing database: {e}")

    async def periodic_maintenance(self):
        """Perform periodic database maintenance"""
        try:
            # Clean up old data
            await self.cleanup_old_data(days_to_keep=30)
            
            # Optimize database
            await self.optimize_database()
            
            # Create backup if needed
            if datetime.now().hour == 2:  # Daily at 2 AM
                await self.create_backup()
            
            logger.info("✅ Periodic maintenance completed")
        except Exception as e:
            logger.error(f"❌ Error in periodic maintenance: {e}")
