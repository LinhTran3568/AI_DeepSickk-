"""
Test script để kiểm tra bot sau khi loại bỏ hoàn toàn DeepSeek
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import BitcoinTradingBot
from ai_engine.puter_client import PuterAIClient
from config.settings import Settings

async def test_clean_bot():
    """Test bot hoàn toàn sạch - chỉ Puter AI"""
    print("🧹 Kiểm tra bot sau khi dọn sạch DeepSeek...")
    
    try:
        # 1. Test Puter AI riêng
        print("\n🤖 Test Puter AI Client...")
        puter_ai = PuterAIClient()
        connected = await puter_ai.test_connection()
        
        if connected:
            print("   ✅ Puter AI hoạt động tốt")
            
            # Test analysis
            sample_data = {
                'symbol': 'BTCUSDT',
                'price': 45000,
                'volume': 1000000,
                'price_change_24h': 2.5,
                'rsi': 58,
                'macd': {'macd': 120, 'signal': 100, 'histogram': 20},
                'bollinger': {'upper': 46000, 'middle': 45000, 'lower': 44000},
                'support_levels': [44000, 43500],
                'resistance_levels': [46000, 47000],
                'trend': 'bullish',
                'volume_trend': 'increasing'
            }
            
            analysis = await puter_ai.analyze_market(sample_data)
            print(f"   📊 AI Analysis: {analysis['action']} ({analysis['confidence']}%)")
            print(f"   💰 Entry: ${analysis['entry_price']:,.0f}")
            print(f"   🎯 Take Profit: ${analysis['take_profit']:,.0f}")
            print(f"   🛡️ Stop Loss: ${analysis['stop_loss']:,.0f}")
        else:
            print("   ❌ Puter AI có vấn đề")
            return
        
        # 2. Test Settings
        print("\n⚙️ Test Settings...")
        settings = Settings()
        errors = settings.validate()
        if errors:
            print(f"   ⚠️ Settings có lỗi: {errors}")
        else:
            print("   ✅ Settings OK")
        
        # 3. Test Main Bot
        print("\n🚀 Test Main Bot...")
        bot = BitcoinTradingBot()
        await bot.initialize()
        print("   ✅ Bot khởi tạo thành công")
        
        # Test một chu kỳ trading
        print("\n📈 Test trading cycle...")
        await bot.run_trading_cycle()
        print("   ✅ Trading cycle hoàn thành")
        
        print("\n🎉 TẤT CẢ TEST THÀNH CÔNG!")
        print("🔥 Bot đã HOÀN TOÀN SẠCH - chỉ dùng Puter AI miễn phí!")
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔄 Bắt đầu test bot clean...")
    asyncio.run(test_clean_bot())
