#!/usr/bin/env python3
"""
Bitcoin AI Trading Bot - Main Entry Point
Hệ thống AI trading bot cho Bitcoin với Puter AI (miễn phí)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from utils.logger import setup_logger
from ai_engine.puter_client import PuterAIClient
from trading.exchange import ExchangeManager
from trading.signals import SignalGenerator
from trading.risk_manager import RiskManager
from data.collector import DataCollector
from utils.notifications import NotificationManager

logger = setup_logger(__name__)

class BitcoinTradingBot:
    """Bitcoin AI Trading Bot chính"""
    
    def __init__(self):
        """Khởi tạo bot"""
        self.settings = Settings()
        
        # Chỉ sử dụng Puter AI - Miễn phí, không cần API key
        self.ai_client = PuterAIClient()
        
        self.exchange = ExchangeManager()
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.data_collector = DataCollector()
        self.notifications = NotificationManager()
        
        self.is_running = False
        
    async def initialize(self):
        """Khởi tạo các component"""
        logger.info("🚀 Đang khởi tạo Bitcoin AI Trading Bot...")
        
        try:
            # Khởi tạo Puter AI - luôn sẵn sàng
            logger.info("🎯 Khởi tạo Puter AI - Miễn phí, không cần API key")
            await self.ai_client.test_connection()
            logger.info("✅ Puter AI sẵn sàng")
            
            # Initialize exchange connection
            await self.exchange.initialize()
            logger.info("✅ Exchange kết nối thành công")
            
            # Setup data collector
            await self.data_collector.initialize()
            logger.info("✅ Data collector sẵn sàng")
            
            # Test notification system
            self.notifications.send_info("Bitcoin AI Trading Bot đã khởi động!")
            logger.info("✅ Notification system hoạt động")
            
            logger.info("🎉 Bot khởi tạo thành công!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo bot: {e}")
            return False
    
    async def run_trading_cycle(self):
        """Chu kỳ trading chính"""
        try:
            # 1. Thu thập dữ liệu market
            market_data = await self.data_collector.get_market_data()
            
            # 2. Phân tích AI với Puter AI
            ai_analysis = await self.ai_client.analyze_market(market_data)
            
            # 3. Tạo signals từ technical analysis
            technical_signals = await self.signal_generator.generate_signals(market_data)
            
            # 4. Kết hợp AI analysis và technical signals
            combined_signal = await self.signal_generator.combine_signals(
                ai_analysis, technical_signals
            )
            
            # 5. Kiểm tra risk management
            risk_check = await self.risk_manager.evaluate_risk(combined_signal)
            
            # 6. Thực hiện trade nếu signal hợp lệ
            if risk_check['approved']:
                trade_result = await self.execute_trade(combined_signal)
                if trade_result:
                    self.notifications.send_trade_alert(trade_result)
            
            # 7. Cập nhật portfolio và metrics
            await self.update_portfolio_metrics()
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong trading cycle: {e}")
            self.notifications.send_error(f"Trading cycle error: {e}")
    
    async def execute_trade(self, signal):
        """Thực hiện giao dịch"""
        try:
            # Calculate position size based on risk management
            position_size = self.risk_manager.calculate_position_size(signal)
            
            # Place order through exchange
            if signal['action'] == 'BUY':
                result = await self.exchange.place_buy_order(
                    symbol=self.settings.TRADING_PAIR,
                    amount=position_size,
                    price=signal['entry_price']
                )
            elif signal['action'] == 'SELL':
                result = await self.exchange.place_sell_order(
                    symbol=self.settings.TRADING_PAIR,
                    amount=position_size,
                    price=signal['entry_price']
                )
            
            logger.info(f"🎯 Trade executed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Lỗi execute trade: {e}")
            return None
    
    async def update_portfolio_metrics(self):
        """Cập nhật metrics portfolio"""
        try:
            balance = await self.exchange.get_balance()
            positions = await self.exchange.get_positions()
            
            # Update portfolio tracking
            # TODO: Implement portfolio metrics calculation
            
        except Exception as e:
            logger.error(f"❌ Lỗi update portfolio: {e}")
    
    async def run(self):
        """Chạy bot chính"""
        if not await self.initialize():
            logger.error("❌ Bot khởi tạo thất bại!")
            return
        
        self.is_running = True
        logger.info("🤖 Bitcoin AI Trading Bot đang chạy...")
        
        try:
            while self.is_running:
                await self.run_trading_cycle()
                
                # Nghỉ giữa các cycle (30 giây)
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("👋 Bot đang dừng...")
        except Exception as e:
            logger.error(f"❌ Lỗi runtime: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Tắt bot an toàn"""
        self.is_running = False
        logger.info("🛑 Bitcoin AI Trading Bot đã dừng")
        self.notifications.send_info("Bot đã dừng hoạt động")

def main():
    """Entry point chính"""
    try:
        # Tạo instance bot
        bot = BitcoinTradingBot()
        
        # Chạy bot
        asyncio.run(bot.run())
        
    except Exception as e:
        print(f"❌ Lỗi khởi động bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
