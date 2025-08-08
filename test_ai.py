"""
Test script để kiểm tra kết nối DeepSeek AI
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.deepseek_client import DeepSeekClient
from config.settings import Settings

async def test_deepseek_connection():
    """Test kết nối với DeepSeek API qua OpenRouter"""
    print("🔄 Đang kiểm tra kết nối DeepSeek AI...")
    
    try:
        # Initialize client
        client = DeepSeekClient()
        settings = Settings()
        
        print(f"📡 API Base URL: {settings.DEEPSEEK_API_BASE}")
        print(f"🤖 Model: {settings.DEEPSEEK_MODEL}")
        print(f"🔑 API Key: {settings.DEEPSEEK_API_KEY[:10]}...{settings.DEEPSEEK_API_KEY[-4:]}")
        
        # Test connection
        result = await client.test_connection()
        
        if result:
            print("✅ Kết nối DeepSeek AI thành công!")
            
            # Test market analysis
            print("\n🧠 Đang test phân tích thị trường...")
            sample_data = {
                'price': 45000,
                'volume': 1500000,
                'rsi': 45,
                'macd': {'macd': 100, 'signal': 90},
                'support_levels': [44000, 43500],
                'resistance_levels': [45500, 46000]
            }
            
            analysis = await client.analyze_market(sample_data)
            
            print("📊 Kết quả phân tích:")
            print(f"   🎯 Action: {analysis.get('action')}")
            print(f"   📈 Confidence: {analysis.get('confidence', 0):.2%}")
            print(f"   💰 Entry Price: ${analysis.get('entry_price', 0):,.2f}")
            print(f"   🛑 Stop Loss: ${analysis.get('stop_loss', 0):,.2f}")
            print(f"   🎯 Take Profit: ${analysis.get('take_profit', 0):,.2f}")
            print(f"   ⚠️ Risk Level: {analysis.get('risk_level')}")
            print(f"   📝 Reasoning: {analysis.get('reasoning')}")
            
            return True
        else:
            print("❌ Kết nối DeepSeek AI thất bại!")
            print("📝 Sẽ sử dụng chế độ fallback (rule-based analysis)")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test AI: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_deepseek_connection())
