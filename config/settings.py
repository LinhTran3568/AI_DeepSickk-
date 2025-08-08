"""
Cấu hình bot trading
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Cài đặt cấu hình bot"""
    
    # API Keys - Chỉ dùng cho binance (không cần cho Puter AI)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bitcoin_bot.db')
    
    # Bot Configuration
    BOT_MODE = os.getenv('BOT_MODE', 'demo')  # demo or live
    TRADING_PAIR = os.getenv('TRADING_PAIR', 'BTC/USDT')
    BASE_CURRENCY = os.getenv('BASE_CURRENCY', 'USDT')
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', '10000'))
    
    # Risk Management
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '5'))  # % of account
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '2'))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '4'))
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
    
    # Technical Analysis
    DEFAULT_TIMEFRAME = os.getenv('DEFAULT_TIMEFRAME', '1h')
    ANALYSIS_TIMEFRAMES = os.getenv('ANALYSIS_TIMEFRAMES', '1m,5m,15m,1h,4h,1d').split(',')
    
    # Dashboard
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Notifications
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    NOTIFICATION_TYPE = os.getenv('NOTIFICATION_TYPE', 'console')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bitcoin_bot.log')
    
    # Trading Parameters
    MIN_CONFIDENCE_SCORE = 0.7  # Minimum confidence for AI signals
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    # Puter AI Configuration - Miễn phí, không cần API key
    PUTER_AI_ENABLED = True
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Puter AI không cần API key - bỏ qua validation cho AI
        
        if cls.BOT_MODE == 'live' and not cls.BINANCE_API_KEY:
            errors.append("BINANCE_API_KEY is required for live trading")
        
        if cls.MAX_POSITION_SIZE > 20:
            errors.append("MAX_POSITION_SIZE should not exceed 20%")
        
        return errors
    
    @classmethod
    def get_project_root(cls) -> Path:
        """Get project root directory"""
        return Path(__file__).parent.parent
