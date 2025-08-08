"""
Exchange Manager - Quản lý kết nối và giao dịch với sàn
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import ccxt.async_support as ccxt
from config.settings import Settings

logger = logging.getLogger(__name__)

class ExchangeManager:
    """Quản lý kết nối exchange và thực hiện giao dịch"""
    
    def __init__(self):
        self.settings = Settings()
        self.exchange = None
        self.is_testnet = self.settings.BINANCE_TESTNET
        self.is_demo = self.settings.BOT_MODE == 'demo'
        
        # Demo trading state
        self.demo_balance = {
            'USDT': self.settings.INITIAL_BALANCE,
            'BTC': 0.0
        }
        self.demo_trades = []
        
    async def initialize(self):
        """Khởi tạo kết nối exchange"""
        try:
            if self.is_demo:
                logger.info("🎮 Initializing DEMO mode - No real trading")
                return True
            
            # Initialize Binance connection
            self.exchange = ccxt.binance({
                'apiKey': self.settings.BINANCE_API_KEY,
                'secret': self.settings.BINANCE_SECRET_KEY,
                'sandbox': self.is_testnet,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # spot trading
                }
            })
            
            # Test connection
            await self.exchange.load_markets()
            balance = await self.exchange.fetch_balance()
            
            logger.info(f"✅ Exchange connected - Balance: ${balance.get('USDT', {}).get('free', 0)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Exchange initialization failed: {e}")
            return False
    
    async def get_current_price(self, symbol: str = None) -> float:
        """Lấy giá hiện tại"""
        try:
            symbol = symbol or self.settings.TRADING_PAIR
            
            if self.is_demo:
                # Get real price even in demo mode for accuracy
                from data.collector import DataCollector
                collector = DataCollector()
                real_price = await collector.get_current_price(symbol)
                return real_price
            
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker['last']
            
        except Exception as e:
            logger.error(f"❌ Error getting price: {e}")
            return 0.0
    
    async def get_balance(self) -> Dict[str, float]:
        """Lấy số dư tài khoản"""
        try:
            if self.is_demo:
                return self.demo_balance.copy()
            
            balance = await self.exchange.fetch_balance()
            return {
                'USDT': balance.get('USDT', {}).get('free', 0),
                'BTC': balance.get('BTC', {}).get('free', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting balance: {e}")
            return {'USDT': 0, 'BTC': 0}
    
    async def place_buy_order(self, symbol: str, amount: float, price: float = None) -> Optional[Dict[str, Any]]:
        """Đặt lệnh mua"""
        try:
            if self.is_demo:
                return await self._demo_buy_order(symbol, amount, price)
            
            if price:
                # Limit order
                order = await self.exchange.create_limit_buy_order(symbol, amount, price)
            else:
                # Market order
                order = await self.exchange.create_market_buy_order(symbol, amount)
            
            logger.info(f"🟢 BUY order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Buy order failed: {e}")
            return None
    
    async def place_sell_order(self, symbol: str, amount: float, price: float = None) -> Optional[Dict[str, Any]]:
        """Đặt lệnh bán"""
        try:
            if self.is_demo:
                return await self._demo_sell_order(symbol, amount, price)
            
            if price:
                # Limit order
                order = await self.exchange.create_limit_sell_order(symbol, amount, price)
            else:
                # Market order
                order = await self.exchange.create_market_sell_order(symbol, amount)
            
            logger.info(f"🔴 SELL order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Sell order failed: {e}")
            return None
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Lấy danh sách positions hiện tại"""
        try:
            if self.is_demo:
                return self._get_demo_positions()
            
            # For spot trading, we check balances
            balance = await self.get_balance()
            positions = []
            
            if balance['BTC'] > 0:
                current_price = await self.get_current_price()
                positions.append({
                    'symbol': 'BTC/USDT',
                    'side': 'long',
                    'amount': balance['BTC'],
                    'entry_price': 0,  # Would need to track this
                    'current_price': current_price,
                    'unrealized_pnl': 0
                })
            
            return positions
            
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    async def get_order_history(self, symbol: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy lịch sử orders"""
        try:
            symbol = symbol or self.settings.TRADING_PAIR
            
            if self.is_demo:
                return self.demo_trades[-limit:]
            
            orders = await self.exchange.fetch_orders(symbol, limit=limit)
            return orders
            
        except Exception as e:
            logger.error(f"❌ Error getting order history: {e}")
            return []
    
    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """Hủy lệnh"""
        try:
            symbol = symbol or self.settings.TRADING_PAIR
            
            if self.is_demo:
                logger.info(f"🚫 DEMO: Cancel order {order_id}")
                return True
            
            result = await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"🚫 Order cancelled: {result}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cancel order failed: {e}")
            return False
    
    async def _demo_buy_order(self, symbol: str, amount: float, price: float = None) -> Dict[str, Any]:
        """Mô phỏng lệnh mua trong demo mode"""
        current_price = price or await self.get_current_price()
        cost = amount * current_price
        
        if self.demo_balance['USDT'] >= cost:
            self.demo_balance['USDT'] -= cost
            self.demo_balance['BTC'] += amount
            
            trade = {
                'id': f"demo_{len(self.demo_trades)}",
                'symbol': symbol,
                'side': 'buy',
                'amount': amount,
                'price': current_price,
                'cost': cost,
                'timestamp': datetime.now().isoformat(),
                'status': 'closed'
            }
            
            self.demo_trades.append(trade)
            logger.info(f"🎮 DEMO BUY: {amount} BTC at ${current_price}")
            return trade
        else:
            raise Exception("Insufficient USDT balance")
    
    async def _demo_sell_order(self, symbol: str, amount: float, price: float = None) -> Dict[str, Any]:
        """Mô phỏng lệnh bán trong demo mode"""
        current_price = price or await self.get_current_price()
        
        if self.demo_balance['BTC'] >= amount:
            self.demo_balance['BTC'] -= amount
            self.demo_balance['USDT'] += amount * current_price
            
            trade = {
                'id': f"demo_{len(self.demo_trades)}",
                'symbol': symbol,
                'side': 'sell',
                'amount': amount,
                'price': current_price,
                'cost': amount * current_price,
                'timestamp': datetime.now().isoformat(),
                'status': 'closed'
            }
            
            self.demo_trades.append(trade)
            logger.info(f"🎮 DEMO SELL: {amount} BTC at ${current_price}")
            return trade
        else:
            raise Exception("Insufficient BTC balance")
    
    def _get_demo_positions(self) -> List[Dict[str, Any]]:
        """Lấy positions trong demo mode"""
        positions = []
        
        if self.demo_balance['BTC'] > 0:
            # Calculate average entry price from trades
            buy_trades = [t for t in self.demo_trades if t['side'] == 'buy']
            if buy_trades:
                total_btc = sum(t['amount'] for t in buy_trades)
                total_cost = sum(t['cost'] for t in buy_trades)
                avg_entry_price = total_cost / total_btc if total_btc > 0 else 0
            else:
                avg_entry_price = 0
            
            positions.append({
                'symbol': 'BTC/USDT',
                'side': 'long',
                'amount': self.demo_balance['BTC'],
                'entry_price': avg_entry_price,
                'current_price': 45000,  # Demo price
                'unrealized_pnl': (45000 - avg_entry_price) * self.demo_balance['BTC']
            })
        
        return positions
    
    async def close(self):
        """Đóng kết nối exchange"""
        if self.exchange:
            await self.exchange.close()
            logger.info("🔌 Exchange connection closed")
