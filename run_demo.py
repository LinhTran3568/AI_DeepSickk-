"""
Demo Script - Test AI Bitcoin Analysis đơn giản
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.deepseek_client import DeepSeekClient

async def run_simple_demo():
    """Chạy demo đơn giản với AI analysis"""
    print("🚀 BITCOIN AI TRADING BOT - DEMO")
    print("=" * 40)
    
    try:
        # 1. Khởi tạo DeepSeek AI
        print("🤖 Khởi tạo DeepSeek AI...")
        deepseek = DeepSeekClient()
        
        # 2. Test kết nối
        print("\n📡 Test kết nối AI...")
        ai_connected = await deepseek.test_connection()
        print(f"   Status: {'✅ AI Connected' if ai_connected else '❌ Fallback Mode'}")
        
        # 3. Tạo dữ liệu giả để test
        print("\n📊 Phân tích thị trường với dữ liệu mẫu...")
        sample_market_data = {
            'price': 67500,  # BTC price
            'volume': 1800000,  # Volume
            'rsi': 42,  # RSI oversold
            'macd': {'macd': 150, 'signal': 120, 'histogram': 30},
            'support_levels': [66000, 65500, 65000],
            'resistance_levels': [68000, 68500, 69000],
            'avg_volume': 1200000
        }
        
        print(f"   � BTC Price: ${sample_market_data['price']:,}")
        print(f"   � RSI: {sample_market_data['rsi']}")
        print(f"   � Volume: {sample_market_data['volume']:,}")
        
        # 4. Chạy AI analysis
        print("\n🧠 Chạy AI analysis...")
        analysis = await deepseek.analyze_market(sample_market_data)
        
        # 5. Hiển thị kết quả
        print("\n🎯 KẾT QUẢ PHÂN TÍCH AI:")
        print("=" * 40)
        print(f"🎯 Action: {analysis.get('action', 'UNKNOWN')}")
        print(f"📈 Confidence: {analysis.get('confidence', 0):.1%}")
        print(f"💰 Entry Price: ${analysis.get('entry_price', 0):,.0f}")
        print(f"🛑 Stop Loss: ${analysis.get('stop_loss', 0):,.0f}")
        print(f"🎯 Take Profit: ${analysis.get('take_profit', 0):,.0f}")
        print(f"⚠️ Risk Level: {analysis.get('risk_level', 'UNKNOWN')}")
        print(f"📝 Reasoning: {analysis.get('reasoning', 'No reason provided')}")
        
        # 6. Tính toán potential return
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
        
        print(f"\n{'='*40}")
        print("✅ Demo hoàn thành!")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🤖 BITCOIN AI TRADING BOT - SIMPLE DEMO")
    print("Nhấn Ctrl+C để dừng\n")
    
    asyncio.run(run_simple_demo())
