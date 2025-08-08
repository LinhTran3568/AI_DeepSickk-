"""
Kiểm tra độ chính xác của technical indicators
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data.collector import DataCollector

async def test_technical_indicators():
    """Kiểm tra technical indicators"""
    print("📈 KIỂM TRA TECHNICAL INDICATORS")
    print("=" * 40)
    
    try:
        data_collector = DataCollector()
        
        # 1. Lấy dữ liệu klines thực
        print("\n📊 1. LẤY DỮ LIỆU KLINES THỰC...")
        klines = await data_collector.get_kline_data('BTCUSDT', '1h', 100)
        
        if klines:
            print(f"   ✅ Lấy được {len(klines)} candles")
            print(f"   📅 Thời gian mới nhất: {klines[-1]['timestamp']}")
            print(f"   💰 Giá đóng mới nhất: ${klines[-1]['close']:,.2f}")
            print(f"   📊 Volume mới nhất: {klines[-1]['volume']:,.2f}")
        else:
            print("   ❌ Không lấy được dữ liệu klines")
            return
        
        # 2. Tính technical indicators
        print(f"\n🔢 2. TÍNH TOÁN TECHNICAL INDICATORS...")
        indicators = await data_collector.calculate_technical_indicators(klines)
        
        # 3. Kiểm tra RSI
        print(f"\n📊 3. RSI (Relative Strength Index):")
        rsi = indicators.get('rsi', 0)
        print(f"   📈 RSI hiện tại: {rsi:.2f}")
        
        if rsi > 70:
            print("   🔴 Overbought (>70) - Có thể giảm")
        elif rsi < 30:
            print("   🟢 Oversold (<30) - Có thể tăng")
        else:
            print("   🟡 Neutral (30-70) - Xu hướng bình thường")
        
        # 4. Kiểm tra MACD
        print(f"\n📊 4. MACD (Moving Average Convergence Divergence):")
        macd = indicators.get('macd', {})
        print(f"   📈 MACD Line: {macd.get('macd', 0):.2f}")
        print(f"   📉 Signal Line: {macd.get('signal', 0):.2f}")
        print(f"   📊 Histogram: {macd.get('histogram', 0):.2f}")
        
        if macd.get('macd', 0) > macd.get('signal', 0):
            print("   🟢 Bullish (MACD > Signal)")
        else:
            print("   🔴 Bearish (MACD < Signal)")
        
        # 5. Kiểm tra Moving Averages
        print(f"\n📊 5. MOVING AVERAGES:")
        ma = indicators.get('moving_averages', {})
        current_price = klines[-1]['close']
        
        for period in ['ma20', 'ma50', 'ma200']:
            ma_value = ma.get(period, 0)
            if ma_value > 0:
                position = "Above" if current_price > ma_value else "Below"
                print(f"   📈 {period.upper()}: ${ma_value:.2f} - Price is {position}")
        
        # 6. Kiểm tra Bollinger Bands
        print(f"\n📊 6. BOLLINGER BANDS:")
        bb = indicators.get('bollinger_bands', {})
        upper = bb.get('upper', 0)
        middle = bb.get('middle', 0)
        lower = bb.get('lower', 0)
        
        print(f"   📈 Upper Band: ${upper:.2f}")
        print(f"   📊 Middle Band: ${middle:.2f}")
        print(f"   📉 Lower Band: ${lower:.2f}")
        
        if current_price > upper:
            print("   🔴 Price above upper band - Overbought")
        elif current_price < lower:
            print("   🟢 Price below lower band - Oversold")
        else:
            print("   🟡 Price within bands - Normal")
        
        # 7. Tính support/resistance
        print(f"\n📊 7. SUPPORT & RESISTANCE LEVELS:")
        sr_levels = data_collector.calculate_support_resistance(klines)
        
        supports = sr_levels.get('support', [])
        resistances = sr_levels.get('resistance', [])
        
        print(f"   🟢 Support levels: {[f'${s:.0f}' for s in supports[:3]]}")
        print(f"   🔴 Resistance levels: {[f'${r:.0f}' for r in resistances[:3]]}")
        
        # 8. Validate với price action
        print(f"\n✅ 8. VALIDATION VỚI PRICE ACTION:")
        
        # Price vs MA validation
        ma20 = ma.get('ma20', 0)
        if ma20 > 0:
            ma_trend = "Bullish" if current_price > ma20 else "Bearish"
            print(f"   📊 MA20 Trend: {ma_trend}")
        
        # Volume validation  
        recent_volumes = [k['volume'] for k in klines[-10:]]
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        current_volume = klines[-1]['volume']
        volume_ratio = current_volume / avg_volume
        
        print(f"   📊 Volume Analysis:")
        print(f"     Current: {current_volume:.2f}")
        print(f"     10-period avg: {avg_volume:.2f}")
        print(f"     Ratio: {volume_ratio:.2f}x")
        
        if volume_ratio > 1.5:
            print("     🔥 High volume - Strong move")
        elif volume_ratio < 0.5:
            print("     💤 Low volume - Weak move")
        else:
            print("     📊 Normal volume")
        
        # 9. Overall assessment
        print(f"\n🎯 9. TỔNG ĐÁNH GIÁ TECHNICAL:")
        
        signals = []
        
        # RSI signal
        if rsi > 70:
            signals.append("RSI Overbought")
        elif rsi < 30:
            signals.append("RSI Oversold")
        
        # MACD signal
        if macd.get('macd', 0) > macd.get('signal', 0):
            signals.append("MACD Bullish")
        else:
            signals.append("MACD Bearish")
        
        # MA signal
        if ma20 > 0 and current_price > ma20:
            signals.append("Above MA20")
        elif ma20 > 0:
            signals.append("Below MA20")
        
        print(f"   📊 Active signals: {', '.join(signals)}")
        
        # 10. Data quality check
        print(f"\n✅ 10. KIỂM TRA CHẤT LƯỢNG DỮ LIỆU:")
        
        quality_checks = []
        quality_checks.append(("Klines data", len(klines) >= 50))
        quality_checks.append(("RSI calculated", 0 <= rsi <= 100))
        quality_checks.append(("MACD calculated", 'macd' in macd))
        quality_checks.append(("MA calculated", ma.get('ma20', 0) > 0))
        quality_checks.append(("Bollinger calculated", bb.get('upper', 0) > bb.get('lower', 0)))
        quality_checks.append(("Support/Resistance", len(supports) > 0 and len(resistances) > 0))
        
        passed = sum(1 for _, check in quality_checks if check)
        total = len(quality_checks)
        
        for name, result in quality_checks:
            status = "✅" if result else "❌"
            print(f"   {status} {name}")
        
        print(f"\n🎯 QUALITY SCORE: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed >= total * 0.8:
            print("🎉 TECHNICAL INDICATORS CHÍNH XÁC VÀ ĐẦY ĐỦ!")
        else:
            print("⚠️ CẦN KIỂM TRA LẠI MỘT SỐ INDICATORS")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_technical_indicators())
