"""
Test Puter AI Client - Không cần API key
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.puter_client import PuterAIClient

async def test_puter_ai():
    """Test Puter AI Client"""
    print("🎯 PUTER AI BITCOIN TRADING BOT TEST")
    print("=" * 40)
    print("🔥 FREE AI - Không cần API key!")
    
    try:
        # Initialize Puter AI client
        print("🤖 Khởi tạo Puter AI...")
        puter_ai = PuterAIClient()
        
        # Test connection
        print("\n📡 Test kết nối AI...")
        ai_connected = await puter_ai.test_connection()
        print(f"   Status: {'✅ AI Connected' if ai_connected else '❌ AI Failed'}")
        
        # Test market analysis
        print("\n📊 Phân tích thị trường với dữ liệu mẫu...")
        sample_market_data = {
            'price': 67500,  # BTC price
            'volume': 1800000,  # Volume
            'rsi': 35,  # RSI oversold - good buy signal
            'macd': {'macd': 150, 'signal': 120, 'histogram': 30},
            'support_levels': [66000, 65500, 65000],
            'resistance_levels': [68000, 68500, 69000],
            'avg_volume': 1200000
        }
        
        print(f"   💰 BTC Price: ${sample_market_data['price']:,}")
        print(f"   📊 RSI: {sample_market_data['rsi']} (Oversold - Good buy opportunity)")
        print(f"   📈 Volume: {sample_market_data['volume']:,}")
        
        # Run AI analysis
        print("\n🧠 Chạy Puter AI analysis...")
        analysis = await puter_ai.analyze_market(sample_market_data)
        
        # Display results
        print("\n🎯 KẾT QUẢ PUTER AI ANALYSIS:")
        print("=" * 40)
        print(f"🎯 Action: {analysis.get('action', 'UNKNOWN')}")
        print(f"📈 Confidence: {analysis.get('confidence', 0):.1%}")
        print(f"💰 Entry Price: ${analysis.get('entry_price', 0):,.0f}")
        print(f"🛑 Stop Loss: ${analysis.get('stop_loss', 0):,.0f}")
        print(f"🎯 Take Profit: ${analysis.get('take_profit', 0):,.0f}")
        print(f"⚠️ Risk Level: {analysis.get('risk_level', 'UNKNOWN')}")
        print(f"📝 Reasoning: {analysis.get('reasoning', 'No reason provided')}")
        
        # Calculate potential return
        entry = analysis.get('entry_price', 0)
        take_profit = analysis.get('take_profit', 0)
        stop_loss = analysis.get('stop_loss', 0)
        
        if entry > 0 and take_profit > 0 and stop_loss > 0:
            if analysis.get('action') == 'BUY':
                profit_pct = ((take_profit - entry) / entry) * 100
                loss_pct = ((entry - stop_loss) / entry) * 100
                risk_reward = profit_pct / loss_pct if loss_pct > 0 else 0
                
                print(f"\n💹 Potential Profit: +{profit_pct:.1f}%")
                print(f"💸 Potential Loss: -{loss_pct:.1f}%")
                print(f"📊 Risk/Reward: 1:{risk_reward:.1f}")
        
        # Test pattern analysis
        print(f"\n🔍 Testing pattern analysis...")
        sample_prices = [67000, 67200, 67100, 67300, 67500, 67400, 67600, 67800, 67700, 67900]
        pattern_result = await puter_ai.analyze_pattern(sample_prices, "1h")
        print(f"   📊 Pattern: {pattern_result.get('pattern', 'unknown')}")
        print(f"   📈 Confidence: {pattern_result.get('confidence', 0):.1%}")
        
        # Test trend prediction
        print(f"\n🔮 Testing trend prediction...")
        historical = {'momentum': 0.025, 'volume_trend': 'increasing'}
        trend_result = await puter_ai.predict_trend(historical)
        print(f"   📈 Trend: {trend_result.get('trend', 'unknown')}")
        print(f"   📊 Confidence: {trend_result.get('confidence', 0):.1%}")
        
        print(f"\n{'='*40}")
        print("✅ Puter AI test hoàn thành!")
        print("🎯 Sẵn sàng trading với AI miễn phí!")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🤖 PUTER AI BITCOIN TRADING BOT")
    print("🔥 FREE AI Analysis - No API Key Required")
    print("Nhấn Ctrl+C để dừng\n")
    
    asyncio.run(test_puter_ai())
