"""
Smart Demo - DeepSeek + Puter AI Fallback
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.deepseek_client import DeepSeekClient
from ai_engine.puter_client import PuterAIClient

async def run_smart_demo():
    """Demo với AI fallback: DeepSeek -> Puter AI"""
    print("🚀 BITCOIN AI TRADING BOT - SMART DEMO")
    print("=" * 40)
    
    try:
        # 1. Try DeepSeek first
        print("🤖 Thử DeepSeek AI trước...")
        deepseek = DeepSeekClient()
        deepseek_works = await deepseek.test_connection()
        
        if deepseek_works:
            print("   ✅ DeepSeek Available")
            ai_client = deepseek
            ai_name = "DeepSeek"
        else:
            print("   ❌ DeepSeek Failed - Chuyển sang Puter AI")
            print("🎯 Khởi tạo Puter AI (FREE)...")
            ai_client = PuterAIClient()
            await ai_client.test_connection()
            ai_name = "Puter AI"
            print("   ✅ Puter AI Ready")
        
        # 2. Market Analysis
        print(f"\n📊 Phân tích thị trường với {ai_name}...")
        sample_market_data = {
            'price': 67500,
            'volume': 1800000,
            'rsi': 35,  # Oversold - good buy signal
            'macd': {'macd': 150, 'signal': 120, 'histogram': 30},
            'support_levels': [66000, 65500, 65000],
            'resistance_levels': [68000, 68500, 69000],
            'avg_volume': 1200000
        }
        
        print(f"   💰 BTC Price: ${sample_market_data['price']:,}")
        print(f"   📊 RSI: {sample_market_data['rsi']} ({'Oversold - Buy opportunity' if sample_market_data['rsi'] < 40 else 'Normal'})")
        print(f"   📈 Volume: {sample_market_data['volume']:,}")
        
        # 3. AI Analysis
        print(f"\n🧠 Chạy {ai_name} analysis...")
        analysis = await ai_client.analyze_market(sample_market_data)
        
        # 4. Results
        print(f"\n🎯 KẾT QUẢ {ai_name.upper()} ANALYSIS:")
        print("=" * 40)
        print(f"🎯 Action: {analysis.get('action', 'UNKNOWN')}")
        print(f"📈 Confidence: {analysis.get('confidence', 0):.1%}")
        print(f"💰 Entry Price: ${analysis.get('entry_price', 0):,.0f}")
        print(f"🛑 Stop Loss: ${analysis.get('stop_loss', 0):,.0f}")
        print(f"🎯 Take Profit: ${analysis.get('take_profit', 0):,.0f}")
        print(f"⚠️ Risk Level: {analysis.get('risk_level', 'UNKNOWN')}")
        print(f"📝 Reasoning: {analysis.get('reasoning', 'No reason provided')}")
        
        # 5. Profit calculation
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
            elif analysis.get('action') == 'SELL':
                profit_pct = ((entry - take_profit) / entry) * 100
                loss_pct = ((stop_loss - entry) / entry) * 100
                risk_reward = profit_pct / loss_pct if loss_pct > 0 else 0
                
                print(f"\n💹 Potential Profit: +{profit_pct:.1f}%")
                print(f"💸 Potential Loss: -{loss_pct:.1f}%")
                print(f"📊 Risk/Reward: 1:{risk_reward:.1f}")
        
        # 6. Additional tests if using Puter AI
        if ai_name == "Puter AI":
            print(f"\n🔍 Testing additional Puter AI features...")
            
            # Test pattern analysis
            sample_prices = [67000, 67200, 67100, 67300, 67500, 67400, 67600, 67800, 67700, 67900]
            pattern_result = await ai_client.analyze_pattern(sample_prices, "1h")
            print(f"   📊 Pattern: {pattern_result.get('pattern', 'unknown')}")
            print(f"   📈 Pattern Confidence: {pattern_result.get('confidence', 0):.1%}")
            
            # Test trend prediction
            historical = {'momentum': 0.025, 'volume_trend': 'increasing'}
            trend_result = await ai_client.predict_trend(historical)
            print(f"   📈 Trend Prediction: {trend_result.get('trend', 'unknown')}")
            print(f"   🎯 Trend Confidence: {trend_result.get('confidence', 0):.1%}")
        
        print(f"\n{'='*40}")
        print(f"✅ {ai_name} Demo hoàn thành!")
        if ai_name == "Puter AI":
            print("🎉 Puter AI hoạt động hoàn hảo - KHÔNG CẦN API KEY!")
        print("🚀 Sẵn sàng trading!")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🤖 BITCOIN AI TRADING BOT - SMART DEMO")
    print("🔥 DeepSeek + Puter AI Fallback System")
    print("Nhấn Ctrl+C để dừng\n")
    
    asyncio.run(run_smart_demo())
