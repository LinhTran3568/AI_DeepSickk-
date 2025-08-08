#!/usr/bin/env python3
"""
Bitcoin AI Trading Bot - Quick Start
"""
import asyncio
import sys
import signal
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import BitcoinTradingBot
from utils.logger import setup_logger

logger = setup_logger(__name__)

class QuickStartBot:
    """Quick start wrapper cho bot"""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Stopping bot gracefully...")
        self.running = False
        if self.bot:
            asyncio.create_task(self.bot.shutdown())
    
    async def run(self):
        """Run bot với error handling"""
        try:
            print("🚀 Bitcoin AI Trading Bot - Quick Start")
            print("=" * 50)
            print("⚠️  Running in DEMO mode (safe testing)")
            print("🌐 Dashboard: http://localhost:5000")
            print("🛑 Press Ctrl+C to stop")
            print("=" * 50)
            
            # Setup signal handler
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # Create and run bot
            self.bot = BitcoinTradingBot()
            self.running = True
            
            await self.bot.run()
            
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            print(f"\n❌ Error: {e}")
        finally:
            if self.bot:
                await self.bot.shutdown()

def main():
    """Main entry point"""
    quick_bot = QuickStartBot()
    asyncio.run(quick_bot.run())

if __name__ == "__main__":
    main()
