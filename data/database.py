"""
Database operations cho Bitcoin Trading Bot
"""
import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import Settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Quản lý database SQLite"""
    
    def __init__(self):
        self.settings = Settings()
        self.db_path = Path("bitcoin_bot.db")
        self.connection = None
        
    async def initialize(self):
        """Khởi tạo database và tạo tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            await self.create_tables()
            logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    async def create_tables(self):
        """Tạo các bảng cần thiết"""
        cursor = self.connection.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                pnl REAL DEFAULT 0,
                fee REAL DEFAULT 0,
                status TEXT NOT NULL,
                signal_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                reasoning TEXT,
                ai_analysis TEXT,
                technical_analysis TEXT,
                executed BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                starting_balance REAL NOT NULL,
                ending_balance REAL NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                rsi REAL,
                macd_data TEXT,
                indicators TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        logger.info("📊 Database tables created/verified")
    
    async def save_trade(self, trade_data: Dict[str, Any]):
        """Lưu thông tin trade"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, symbol, side, amount, price, cost, 
                    pnl, fee, status, signal_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('timestamp'),
                trade_data.get('symbol'),
                trade_data.get('side'),
                trade_data.get('amount'),
                trade_data.get('price'),
                trade_data.get('cost'),
                trade_data.get('pnl', 0),
                trade_data.get('fee', 0),
                trade_data.get('status'),
                json.dumps(trade_data.get('signal_data', {}))
            ))
            
            self.connection.commit()
            logger.info(f"💾 Trade saved to database: {trade_data.get('side')} {trade_data.get('amount')} at ${trade_data.get('price')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save trade: {e}")
    
    async def save_signal(self, signal_data: Dict[str, Any]):
        """Lưu thông tin signal"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO signals (
                    timestamp, action, confidence, entry_price, stop_loss, 
                    take_profit, reasoning, ai_analysis, technical_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_data.get('timestamp'),
                signal_data.get('action'),
                signal_data.get('confidence'),
                signal_data.get('entry_price'),
                signal_data.get('stop_loss'),
                signal_data.get('take_profit'),
                signal_data.get('reasoning'),
                json.dumps(signal_data.get('ai_component', {})),
                json.dumps(signal_data.get('technical_component', {}))
            ))
            
            self.connection.commit()
            logger.info(f"📡 Signal saved: {signal_data.get('action')} - {signal_data.get('confidence'):.2%}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save signal: {e}")
    
    async def save_market_data(self, market_data: Dict[str, Any]):
        """Lưu market data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO market_data (
                    timestamp, symbol, price, volume, rsi, macd_data, indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                market_data.get('timestamp'),
                market_data.get('symbol'),
                market_data.get('price'),
                market_data.get('volume'),
                market_data.get('rsi'),
                json.dumps(market_data.get('macd', {})),
                json.dumps({k: v for k, v in market_data.items() if k not in ['timestamp', 'symbol', 'price', 'volume', 'rsi', 'macd']})
            ))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to save market data: {e}")
    
    async def get_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách trades"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            trades = []
            for row in cursor.fetchall():
                trade = dict(row)
                if trade['signal_data']:
                    trade['signal_data'] = json.loads(trade['signal_data'])
                trades.append(trade)
            
            return trades
            
        except Exception as e:
            logger.error(f"❌ Failed to get trades: {e}")
            return []
    
    async def get_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách signals"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM signals 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            signals = []
            for row in cursor.fetchall():
                signal = dict(row)
                if signal['ai_analysis']:
                    signal['ai_analysis'] = json.loads(signal['ai_analysis'])
                if signal['technical_analysis']:
                    signal['technical_analysis'] = json.loads(signal['technical_analysis'])
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to get signals: {e}")
            return []
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Lấy thống kê performance"""
        try:
            cursor = self.connection.cursor()
            
            # Total trades
            cursor.execute('SELECT COUNT(*) as total_trades FROM trades')
            total_trades = cursor.fetchone()['total_trades']
            
            # Winning/losing trades
            cursor.execute('SELECT COUNT(*) as winning FROM trades WHERE pnl > 0')
            winning_trades = cursor.fetchone()['winning']
            
            cursor.execute('SELECT COUNT(*) as losing FROM trades WHERE pnl < 0')
            losing_trades = cursor.fetchone()['losing']
            
            # Total P&L
            cursor.execute('SELECT SUM(pnl) as total_pnl FROM trades')
            total_pnl = cursor.fetchone()['total_pnl'] or 0
            
            # Best/worst trades
            cursor.execute('SELECT MAX(pnl) as best, MIN(pnl) as worst FROM trades')
            result = cursor.fetchone()
            best_trade = result['best'] or 0
            worst_trade = result['worst'] or 0
            
            # Win rate
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'best_trade': best_trade,
                'worst_trade': worst_trade
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance stats: {e}")
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'best_trade': 0,
                'worst_trade': 0
            }
    
    async def cleanup_old_data(self, days: int = 30):
        """Dọn dẹp dữ liệu cũ"""
        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now().strftime('%Y-%m-%d')
            
            # Keep only recent market data
            cursor.execute('''
                DELETE FROM market_data 
                WHERE created_at < datetime('now', '-30 days')
            ''')
            
            self.connection.commit()
            logger.info(f"🧹 Cleaned up old data (older than {days} days)")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")
    
    async def close(self):
        """Đóng kết nối database"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Database connection closed")
