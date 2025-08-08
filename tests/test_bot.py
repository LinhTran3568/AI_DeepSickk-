"""
Test cases cho Bitcoin Trading Bot
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from trading.exchange import ExchangeManager
from trading.risk_manager import RiskManager
from ai_engine.deepseek_client import DeepSeekClient
from data.collector import DataCollector

class TestSettings:
    """Test Settings configuration"""
    
    def test_settings_initialization(self):
        """Test settings can be initialized"""
        settings = Settings()
        assert settings.TRADING_PAIR == 'BTC/USDT'
        assert settings.BOT_MODE in ['demo', 'live']
        assert isinstance(settings.MAX_POSITION_SIZE, (int, float))
    
    def test_settings_validation(self):
        """Test settings validation"""
        errors = Settings.validate()
        # Should have error for missing API key in test environment
        assert isinstance(errors, list)

class TestExchangeManager:
    """Test Exchange Manager"""
    
    def setup_method(self):
        """Setup for each test"""
        self.exchange = ExchangeManager()
    
    @pytest.mark.asyncio
    async def test_demo_mode_initialization(self):
        """Test demo mode initialization"""
        # Force demo mode
        self.exchange.is_demo = True
        result = await self.exchange.initialize()
        assert result == True
    
    @pytest.mark.asyncio
    async def test_demo_balance(self):
        """Test demo balance retrieval"""
        self.exchange.is_demo = True
        balance = await self.exchange.get_balance()
        assert 'USDT' in balance
        assert 'BTC' in balance
        assert balance['USDT'] == 10000  # Initial balance
    
    @pytest.mark.asyncio
    async def test_demo_price(self):
        """Test demo price retrieval"""
        self.exchange.is_demo = True
        price = await self.exchange.get_current_price()
        assert isinstance(price, (int, float))
        assert price > 0

class TestRiskManager:
    """Test Risk Manager"""
    
    def setup_method(self):
        """Setup for each test"""
        self.risk_manager = RiskManager()
    
    @pytest.mark.asyncio
    async def test_confidence_check(self):
        """Test confidence checking"""
        signal = {'confidence': 0.8, 'action': 'BUY', 'entry_price': 45000}
        evaluation = await self.risk_manager.evaluate_risk(signal)
        assert 'approved' in evaluation
        assert isinstance(evaluation['approved'], bool)
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        signal = {
            'confidence': 0.8,
            'entry_price': 45000,
            'stop_loss': 44100,
            'take_profit': 46800
        }
        position_size = self.risk_manager.calculate_position_size(signal, 10000)
        assert isinstance(position_size, (int, float))
        assert position_size > 0

class TestDeepSeekClient:
    """Test DeepSeek Client"""
    
    def setup_method(self):
        """Setup for each test"""
        self.deepseek = DeepSeekClient()
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        assert self.deepseek.api_key is not None
        assert self.deepseek.base_url is not None
    
    def test_prompt_creation(self):
        """Test market analysis prompt creation"""
        market_data = {
            'price': 45000,
            'volume': 1000000,
            'rsi': 50,
            'macd': {'macd': 100, 'signal': 80},
            'support_levels': [44000],
            'resistance_levels': [46000]
        }
        prompt = self.deepseek._create_market_analysis_prompt(market_data)
        assert isinstance(prompt, str)
        assert 'Bitcoin' in prompt or 'BTC' in prompt

class TestDataCollector:
    """Test Data Collector"""
    
    def setup_method(self):
        """Setup for each test"""
        self.data_collector = DataCollector()
    
    def test_technical_indicators(self):
        """Test technical indicators calculation"""
        prices = [45000 + i*10 for i in range(50)]  # Mock price data
        
        # Test RSI calculation
        rsi = self.data_collector._calculate_rsi(prices)
        assert 0 <= rsi <= 100
        
        # Test SMA calculation
        sma = self.data_collector._calculate_sma(prices, 20)
        assert isinstance(sma, (int, float))
        assert sma > 0
    
    def test_support_resistance_calculation(self):
        """Test S/R levels calculation"""
        klines = []
        base_price = 45000
        
        # Create mock kline data
        for i in range(50):
            price = base_price + (i * 10) + ((-1)**i * 100)
            klines.append({
                'high': price + 50,
                'low': price - 50,
                'close': price
            })
        
        sr_levels = self.data_collector.calculate_support_resistance(klines)
        assert 'support' in sr_levels
        assert 'resistance' in sr_levels
        assert isinstance(sr_levels['support'], list)
        assert isinstance(sr_levels['resistance'], list)

@pytest.mark.asyncio
async def test_integration_demo_trading():
    """Integration test for demo trading flow"""
    # Initialize components
    exchange = ExchangeManager()
    exchange.is_demo = True
    
    risk_manager = RiskManager()
    
    # Test initialization
    init_result = await exchange.initialize()
    assert init_result == True
    
    # Test balance
    initial_balance = await exchange.get_balance()
    assert initial_balance['USDT'] == 10000
    
    # Test demo buy order
    trade_result = await exchange.place_buy_order('BTC/USDT', 0.001, 45000)
    assert trade_result is not None
    assert trade_result['side'] == 'buy'
    
    # Check balance after trade
    after_balance = await exchange.get_balance()
    assert after_balance['USDT'] < initial_balance['USDT']
    assert after_balance['BTC'] > 0
    
    # Test positions
    positions = await exchange.get_positions()
    assert len(positions) > 0

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
