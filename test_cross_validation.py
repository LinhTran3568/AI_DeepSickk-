"""
Cross-validation test - So sánh dữ liệu với nhiều nguồn
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def cross_validate_btc_price():
    """So sánh giá BTC từ nhiều nguồn"""
    print("🔄 CROSS-VALIDATION TEST - SO SÁNH NHIỀU NGUỒN")
    print("=" * 55)
    
    sources = {}
    
    try:
        # 1. Binance API (nguồn chính của bot)
        print("\n📊 1. BINANCE API...")
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT') as response:
                if response.status == 200:
                    data = await response.json()
                    sources['Binance'] = float(data['price'])
                    print(f"   ✅ Binance: ${sources['Binance']:,.2f}")
        
        # 2. CoinGecko API
        print("\n🦎 2. COINGECKO API...")
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd') as response:
                if response.status == 200:
                    data = await response.json()
                    sources['CoinGecko'] = float(data['bitcoin']['usd'])
                    print(f"   ✅ CoinGecko: ${sources['CoinGecko']:,.2f}")
        
        # 3. Coinbase API
        print("\n🔵 3. COINBASE API...")
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC') as response:
                if response.status == 200:
                    data = await response.json()
                    sources['Coinbase'] = float(data['data']['rates']['USD'])
                    print(f"   ✅ Coinbase: ${sources['Coinbase']:,.2f}")
        
        # 4. CryptoCompare API
        print("\n📈 4. CRYPTOCOMPARE API...")
        async with aiohttp.ClientSession() as session:
            async with session.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD') as response:
                if response.status == 200:
                    data = await response.json()
                    sources['CryptoCompare'] = float(data['USD'])
                    print(f"   ✅ CryptoCompare: ${sources['CryptoCompare']:,.2f}")
        
        # 5. Phân tích độ chênh lệch
        print(f"\n📊 5. PHÂN TÍCH ĐỘ CHÊNH LỆCH:")
        
        if len(sources) > 1:
            prices = list(sources.values())
            avg_price = sum(prices) / len(prices)
            max_price = max(prices)
            min_price = min(prices)
            spread = max_price - min_price
            spread_percent = (spread / avg_price) * 100
            
            print(f"   📊 Giá trung bình: ${avg_price:,.2f}")
            print(f"   📈 Giá cao nhất: ${max_price:,.2f}")
            print(f"   📉 Giá thấp nhất: ${min_price:,.2f}")
            print(f"   📊 Spread: ${spread:,.2f} ({spread_percent:.3f}%)")
            
            print(f"\n📋 CHI TIẾT ĐỘ CHÊNH LỆCH:")
            for source, price in sources.items():
                diff = price - avg_price
                diff_percent = (diff / avg_price) * 100
                symbol = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
                print(f"   {symbol} {source:12}: ${price:>10,.2f} ({diff_percent:+.3f}%)")
            
            # 6. Đánh giá độ tin cậy
            print(f"\n🎯 6. ĐÁNH GIÁ ĐỘ TIN CẬY:")
            
            if spread_percent < 0.1:
                print("   ✅ RẤT TIN CẬY: Tất cả nguồn đều khá nhất quán")
            elif spread_percent < 0.5:
                print("   ✅ TIN CẬY: Độ chênh lệch trong giới hạn cho phép")
            elif spread_percent < 1.0:
                print("   ⚠️ TRUNG BÌNH: Có chênh lệch nhỏ giữa các nguồn")
            else:
                print("   ❌ CẨN THẬN: Chênh lệch lớn giữa các nguồn")
            
            # 7. Đề xuất nguồn chính
            print(f"\n🎯 7. ĐÁNH GIÁ NGUỒN DỮ LIỆU BOT:")
            
            if 'Binance' in sources:
                binance_diff = abs(sources['Binance'] - avg_price)
                binance_diff_percent = (binance_diff / avg_price) * 100
                
                print(f"   🤖 Bot sử dụng: Binance")
                print(f"   📊 Giá Binance: ${sources['Binance']:,.2f}")
                print(f"   📊 Độ lệch so với TB: {binance_diff_percent:.3f}%")
                
                if binance_diff_percent < 0.1:
                    print("   ✅ XUẤT SẮC: Binance rất chính xác")
                elif binance_diff_percent < 0.3:
                    print("   ✅ TỐT: Binance trong ngưỡng chấp nhận")
                else:
                    print("   ⚠️ CẦN THEO DÕI: Binance có chênh lệch")
        
        # 8. Timestamp và freshness
        print(f"\n⏰ 8. THÔNG TIN THỜI GIAN:")
        print(f"   📅 Thời gian kiểm tra: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🔄 Tần suất cập nhật khuyến nghị: 30-60 giây")
        
        # 9. Lưu kết quả
        result = {
            'timestamp': datetime.now().isoformat(),
            'sources': sources,
            'analysis': {
                'avg_price': avg_price if len(sources) > 1 else 0,
                'spread': spread if len(sources) > 1 else 0,
                'spread_percent': spread_percent if len(sources) > 1 else 0
            }
        }
        
        with open('price_cross_validation.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 9. KẾT QUẢ:")
        print("   ✅ Đã lưu kết quả vào price_cross_validation.json")
        print("   🎯 Cross-validation hoàn thành!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH CROSS-VALIDATION: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(cross_validate_btc_price())
