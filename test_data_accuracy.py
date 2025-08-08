"""
Test script để kiểm tra tính chính xác của dữ liệu thị trường
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.collector import DataCollector
from ai_engine.puter_client import PuterAIClient
from trading.exchange import ExchangeManager

async def test_real_data_accuracy():
    """Kiểm tra tính chính xác của dữ liệu thực"""
    print("🔍 KIỂM TRA TÍNH CHÍNH XÁC DỮ LIỆU THỰC")
    print("=" * 50)
    
    try:
        # 1. Khởi tạo data collector
        print("\n📊 1. KIỂM TRA DATA COLLECTOR...")
        data_collector = DataCollector()
        await data_collector.initialize()
        
        # 2. Lấy dữ liệu thực từ Binance
        print("\n🔗 2. LẤY DỮ LIỆU THỰC TỪ BINANCE API...")
        market_data = await data_collector.get_market_data('BTCUSDT')
        
        # In chi tiết dữ liệu
        print(f"   Symbol: {market_data['symbol']}")
        print(f"   📅 Timestamp: {market_data['timestamp']}")
        print(f"   💰 Current Price: ${market_data['price']:,.2f}")
        print(f"   📈 24h High: ${market_data['high_24h']:,.2f}")
        print(f"   📉 24h Low: ${market_data['low_24h']:,.2f}")
        print(f"   📊 24h Volume: {market_data['volume']:,.0f} BTC")
        print(f"   💸 24h Quote Volume: ${market_data['volume_quote']:,.0f}")
        print(f"   🔄 24h Change: {market_data['price_change_percent_24h']:+.2f}%")
        
        # 3. Kiểm tra chỉ báo kỹ thuật
        print(f"\n📈 3. CHỈ BÁAO KỸ THUẬT (dựa trên dữ liệu thực):")
        print(f"   RSI: {market_data.get('rsi', 'N/A')}")
        print(f"   MACD: {market_data.get('macd', {})}")
        print(f"   MA20: ${market_data.get('moving_averages', {}).get('ma20', 0):,.2f}")
        print(f"   MA50: ${market_data.get('moving_averages', {}).get('ma50', 0):,.2f}")
        print(f"   Bollinger Upper: ${market_data.get('bollinger_bands', {}).get('upper', 0):,.2f}")
        print(f"   Bollinger Lower: ${market_data.get('bollinger_bands', {}).get('lower', 0):,.2f}")
        
        # 4. Kiểm tra support/resistance
        print(f"\n📊 4. SUPPORT/RESISTANCE LEVELS:")
        print(f"   Support Levels: {[f'${s:,.0f}' for s in market_data.get('support_levels', [])]}")
        print(f"   Resistance Levels: {[f'${r:,.0f}' for r in market_data.get('resistance_levels', [])]}")
        
        # 5. Verify với API trực tiếp
        print(f"\n✅ 5. XÁC THỰC VỚI API TRỰC TIẾP...")
        current_price = await data_collector.get_current_price('BTCUSDT')
        ticker_data = await data_collector.get_24h_ticker('BTCUSDT')
        
        print(f"   Direct API Price: ${current_price:,.2f}")
        print(f"   Market Data Price: ${market_data['price']:,.2f}")
        print(f"   Price Difference: ${abs(current_price - market_data['price']):,.2f}")
        
        # 6. Test AI analysis với dữ liệu thực
        print(f"\n🤖 6. PHÂN TÍCH AI VỚI DỮ LIỆU THỰC...")
        puter_ai = PuterAIClient()
        ai_analysis = await puter_ai.analyze_market(market_data)
        
        print(f"   AI Action: {ai_analysis['action']}")
        print(f"   AI Confidence: {ai_analysis['confidence']}%")
        print(f"   Entry Price: ${ai_analysis['entry_price']:,.2f}")
        print(f"   Take Profit: ${ai_analysis['take_profit']:,.2f}")
        print(f"   Stop Loss: ${ai_analysis['stop_loss']:,.2f}")
        
        # Calculate risk/reward ratio
        risk = abs(ai_analysis['entry_price'] - ai_analysis['stop_loss'])
        reward = abs(ai_analysis['take_profit'] - ai_analysis['entry_price'])
        rr_ratio = reward / risk if risk > 0 else 0
        print(f"   Risk/Reward Ratio: {rr_ratio:.2f}")
        
        # 7. Kiểm tra Exchange Manager
        print(f"\n🏪 7. KIỂM TRA EXCHANGE MANAGER...")
        exchange = ExchangeManager()
        await exchange.initialize()
        
        balance = await exchange.get_balance()
        print(f"   Account Balance: {balance}")
        
        # 8. Validate data freshness
        print(f"\n⏰ 8. KIỂM TRA ĐỘ TƯƠI CỦA DỮ LIỆU...")
        timestamp = datetime.fromisoformat(market_data['timestamp'].replace('Z', '+00:00'))
        now = datetime.now()
        age_seconds = (now - timestamp.replace(tzinfo=None)).total_seconds()
        
        print(f"   Data Age: {age_seconds:.1f} seconds")
        if age_seconds < 60:
            print("   ✅ Dữ liệu rất tươi (< 1 phút)")
        elif age_seconds < 300:
            print("   ⚠️ Dữ liệu hơi cũ (< 5 phút)")
        else:
            print("   ❌ Dữ liệu quá cũ (> 5 phút)")
        
        # 9. Tổng kết
        print(f"\n📋 9. TỔNG KẾT ĐÁNH GIÁ:")
        
        checks = []
        checks.append(("Kết nối API Binance", market_data['price'] > 0))
        checks.append(("Dữ liệu ticker 24h", len(ticker_data) > 0))
        checks.append(("Chỉ báo kỹ thuật", 'rsi' in market_data))
        checks.append(("Support/Resistance", len(market_data.get('support_levels', [])) > 0))
        checks.append(("AI Analysis", ai_analysis['confidence'] > 50))
        checks.append(("Dữ liệu tươi", age_seconds < 300))
        
        passed = sum(1 for _, check in checks if check)
        total = len(checks)
        
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {name}")
        
        print(f"\n🎯 KẾT QUẢ: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
        
        if passed >= total * 0.8:  # 80% threshold
            print("🎉 DỮ LIỆU CHÍNH XÁC VÀ TIN CẬY!")
        else:
            print("⚠️ CẦN KIỂM TRA LẠI MỘT SỐ THÀNH PHẦN")
        
        # 10. Raw data export for verification
        print(f"\n💾 10. XUẤT DỮ LIỆU RAW ĐỂ XÁC THỰC...")
        with open('market_data_verification.json', 'w') as f:
            json.dump(market_data, f, indent=2, default=str)
        print("   ✅ Đã lưu vào market_data_verification.json")
        
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH KIỂM TRA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Bắt đầu kiểm tra tính chính xác dữ liệu...")
    asyncio.run(test_real_data_accuracy())
