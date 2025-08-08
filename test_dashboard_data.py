"""
Quick test to verify dashboard real-time updates
"""

import asyncio
from data.collector import DataCollector

async def test_real_data():
    """Test if we can get real data"""
    print("🔄 Testing real data for dashboard...")
    
    try:
        collector = DataCollector()
        market_data = await collector.get_market_data('BTCUSDT')
        
        if market_data:
            print(f"✅ Real data obtained:")
            print(f"   Price: ${market_data['price']:,.2f}")
            print(f"   Volume: {market_data['volume']:,.2f}")
            print(f"   24h Change: {market_data['price_change_percent_24h']:+.2f}%")
            print(f"   Timestamp: {market_data['timestamp']}")
            print("\n🎯 Dashboard should now show real data!")
        else:
            print("❌ No market data received")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_data())
