#!/usr/bin/env python3
"""
Bitcoin AI Trading Bot - Demo Script
Chạy demo nhanh để test các chức năng chính
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from utils.logger import setup_logger
from ai_engine.deepseek_client import DeepSeekClient
from trading.exchange import ExchangeManager
from trading.signals import SignalGenerator
from trading.risk_manager import RiskManager
from data.collector import DataCollector
from utils.notifications import NotificationManager

logger = setup_logger(__name__)

async def demo_ai_analysis():
    """Demo AI analysis với DeepSeek"""
    print("\n" + "="*50)
    print("🧠 DEMO: AI Analysis với DeepSeek")
    print("="*50)
    
    try:
        deepseek = DeepSeekClient()
        
        # Test connection
        print("📡 Testing DeepSeek API connection...")
        connected = await deepseek.test_connection()
        
        if connected:
            print("✅ DeepSeek API connected successfully!")
            
            # Mock market data
            market_data = {
                'price': 45000,
                'volume': 1500000,
                'rsi': 35,  # Oversold
                'macd': {'macd': 150, 'signal': 120, 'histogram': 30},
                'support_levels': [44000, 43500],
                'resistance_levels': [45500, 46000]
            }
            
            print("🔍 Analyzing market with AI...")
            analysis = await deepseek.analyze_market(market_data)
            
            print(f"📊 AI Analysis Result:")
            print(f"   Action: {analysis.get('action', 'N/A')}")
            print(f"   Confidence: {analysis.get('confidence', 0):.2%}")
            print(f"   Entry Price: ${analysis.get('entry_price', 0):,.2f}")
            print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
            
        else:
            print("❌ DeepSeek API connection failed!")
            
    except Exception as e:
        print(f"❌ AI Analysis demo failed: {e}")

async def demo_exchange_operations():
    """Demo exchange operations"""
    print("\n" + "="*50)
    print("💱 DEMO: Exchange Operations")
    print("="*50)
    
    try:
        exchange = ExchangeManager()
        
        # Initialize (demo mode)
        print("🎮 Initializing Exchange (Demo Mode)...")
        initialized = await exchange.initialize()
        
        if initialized:
            print("✅ Exchange initialized!")
            
            # Get balance
            balance = await exchange.get_balance()
            print(f"💰 Current Balance:")
            print(f"   USDT: ${balance['USDT']:,.2f}")
            print(f"   BTC: {balance['BTC']:.6f}")
            
            # Get current price
            price = await exchange.get_current_price()
            print(f"📈 Current BTC Price: ${price:,.2f}")
            
            # Demo trade
            print("🔄 Executing Demo Buy Order...")
            trade_result = await exchange.place_buy_order('BTC/USDT', 0.001, price)
            
            if trade_result:
                print(f"✅ Trade executed: {trade_result['side'].upper()} {trade_result['amount']} BTC at ${trade_result['price']:,.2f}")
                
                # Check new balance
                new_balance = await exchange.get_balance()
                print(f"💰 New Balance:")
                print(f"   USDT: ${new_balance['USDT']:,.2f}")
                print(f"   BTC: {new_balance['BTC']:.6f}")
            
        else:
            print("❌ Exchange initialization failed!")
            
    except Exception as e:
        print(f"❌ Exchange demo failed: {e}")

async def demo_signal_generation():
    """Demo signal generation"""
    print("\n" + "="*50)
    print("📡 DEMO: Trading Signal Generation")
    print("="*50)
    
    try:
        signal_generator = SignalGenerator()
        
        # Mock market data
        market_data = {
            'price': 45000,
            'volume': 1500000,
            'avg_volume': 1200000,
            'rsi': 35,  # Oversold
            'macd': {
                'macd': 150,
                'signal': 120,
                'histogram': 30
            },
            'moving_averages': {
                'sma_20': 44800,
                'sma_50': 44500,
                'ema_12': 44950,
                'ema_26': 44700,
                'current_price': 45000
            },
            'support_levels': [44000, 43500],
            'resistance_levels': [45500, 46000]
        }
        
        print("📊 Generating technical signals...")
        technical_signals = await signal_generator.generate_signals(market_data)
        
        print(f"🔍 Technical Analysis:")
        print(f"   Action: {technical_signals.get('action', 'N/A')}")
        print(f"   Confidence: {technical_signals.get('confidence', 0):.2%}")
        print(f"   Key Indicators: {', '.join(technical_signals.get('key_indicators', []))}")
        print(f"   Reasoning: {technical_signals.get('reasoning', 'N/A')}")
        
        # Mock AI analysis
        ai_analysis = {
            'action': 'BUY',
            'confidence': 0.82,
            'entry_price': 45000,
            'stop_loss': 44100,
            'take_profit': 46800,
            'reasoning': 'Strong bullish pattern detected with high volume confirmation'
        }
        
        print("🤖 Combining with AI analysis...")
        combined_signal = await signal_generator.combine_signals(ai_analysis, technical_signals)
        
        print(f"🎯 Final Combined Signal:")
        print(f"   Action: {combined_signal.get('action', 'N/A')}")
        print(f"   Confidence: {combined_signal.get('confidence', 0):.2%}")
        print(f"   Entry: ${combined_signal.get('entry_price', 0):,.2f}")
        print(f"   Stop Loss: ${combined_signal.get('stop_loss', 0):,.2f}")
        print(f"   Take Profit: ${combined_signal.get('take_profit', 0):,.2f}")
        
    except Exception as e:
        print(f"❌ Signal generation demo failed: {e}")

async def demo_risk_management():
    """Demo risk management"""
    print("\n" + "="*50)
    print("🛡️ DEMO: Risk Management")
    print("="*50)
    
    try:
        risk_manager = RiskManager()
        
        # Mock signal
        signal = {
            'action': 'BUY',
            'confidence': 0.82,
            'entry_price': 45000,
            'stop_loss': 44100,
            'take_profit': 46800,
            'risk_level': 'MEDIUM'
        }
        
        print("🔍 Evaluating trade risk...")
        risk_evaluation = await risk_manager.evaluate_risk(signal)
        
        print(f"📋 Risk Assessment:")
        print(f"   Approved: {'✅ YES' if risk_evaluation['approved'] else '❌ NO'}")
        print(f"   Confidence Score: {risk_evaluation['confidence_score']:.2%}")
        print(f"   Recommendation: {risk_evaluation['recommendation']}")
        
        if risk_evaluation['approved']:
            # Calculate position size
            position_size = risk_manager.calculate_position_size(signal, 10000)
            print(f"💰 Position Sizing:")
            print(f"   Recommended Size: {position_size:.6f} BTC")
            print(f"   USD Value: ${position_size * signal['entry_price']:,.2f}")
            print(f"   Risk Amount: ${abs(signal['entry_price'] - signal['stop_loss']) * position_size:.2f}")
        
    except Exception as e:
        print(f"❌ Risk management demo failed: {e}")

def demo_notifications():
    """Demo notification system"""
    print("\n" + "="*50)
    print("🔔 DEMO: Notification System")
    print("="*50)
    
    try:
        notifications = NotificationManager()
        
        print("📢 Testing notification system...")
        
        # Test different types of notifications
        notifications.send_info("Bot started successfully!")
        
        # Test trade alert
        test_trade = {
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'amount': 0.001,
            'price': 45000
        }
        notifications.send_trade_alert(test_trade)
        
        # Test signal alert
        test_signal = {
            'action': 'BUY',
            'confidence': 0.85,
            'entry_price': 45000,
            'stop_loss': 44100,
            'take_profit': 46800,
            'reason': 'AI prediction + RSI oversold + Volume spike'
        }
        notifications.send_signal_alert(test_signal)
        
        print("✅ Notification system working!")
        
    except Exception as e:
        print(f"❌ Notification demo failed: {e}")

async def run_full_demo():
    """Chạy demo đầy đủ"""
    print("🚀 BITCOIN AI TRADING BOT - FULL DEMO")
    print("=" * 60)
    
    # Check settings
    print("⚙️ Checking configuration...")
    settings = Settings()
    errors = settings.validate()
    
    if errors:
        print("⚠️ Configuration warnings:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuration OK!")
    
    # Run demos
    demo_notifications()
    await demo_exchange_operations()
    await demo_signal_generation()
    await demo_risk_management()
    await demo_ai_analysis()
    
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETED!")
    print("="*60)
    print("📋 Next Steps:")
    print("   1. Review the demo results above")
    print("   2. Configure your API keys in .env file")
    print("   3. Run: python main.py (for trading bot)")
    print("   4. Run: python dashboard.py (for web dashboard)")
    print("   5. Open browser: http://localhost:5000")
    print("\n⚠️ Remember: Always start with DEMO mode!")

def main():
    """Main demo function"""
    try:
        asyncio.run(run_full_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
