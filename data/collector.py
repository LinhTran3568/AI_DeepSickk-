"""
Data Collector - Thu thập và xử lý dữ liệu thị trường Bitcoin
"""
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from config.settings import Settings

logger = logging.getLogger(__name__)

class DataCollector:
    """Thu thập dữ liệu thị trường"""
    
    def __init__(self):
        self.settings = Settings()
        self.api_endpoints = {
            'binance': 'https://api.binance.com/api/v3',
            'coingecko': 'https://api.coingecko.com/api/v3',
            'coinmarketcap': 'https://pro-api.coinmarketcap.com/v1'
        }
        
        # Cache để tránh call API quá nhiều
        self.price_cache = {}
        self.cache_timeout = 30  # 30 seconds
        
    async def initialize(self):
        """Khởi tạo data collector"""
        try:
            # Test API connections
            await self._test_api_connections()
            logger.info("✅ Data collector initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data collector initialization failed: {e}")
            return False
    
    async def get_market_data(self, symbol: str = 'BTCUSDT') -> Dict[str, Any]:
        """
        Thu thập dữ liệu thị trường đầy đủ
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Complete market data
        """
        try:
            # Parallel data collection
            tasks = [
                self.get_current_price(symbol),
                self.get_24h_ticker(symbol),
                self.get_orderbook(symbol),
                self.get_recent_trades(symbol),
                self.get_kline_data(symbol, '1h', 100)
            ]
            
            price, ticker, orderbook, trades, klines = await asyncio.gather(*tasks)
            
            # Calculate technical indicators
            technical_data = await self.calculate_technical_indicators(klines)
            
            # Support/Resistance levels
            sr_levels = self.calculate_support_resistance(klines)
            
            market_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'price': price,
                'volume': ticker.get('volume', 0),
                'volume_quote': ticker.get('quoteVolume', 0),
                'high_24h': ticker.get('high', price),
                'low_24h': ticker.get('low', price),
                'price_change_24h': ticker.get('priceChange', 0),
                'price_change_percent_24h': ticker.get('priceChangePercent', 0),
                'bid_price': orderbook.get('bids', [[0]])[0][0] if orderbook.get('bids') else price,
                'ask_price': orderbook.get('asks', [[0]])[0][0] if orderbook.get('asks') else price,
                'spread': self._calculate_spread(orderbook),
                'avg_volume': self._calculate_avg_volume(klines),
                'support_levels': sr_levels['support'],
                'resistance_levels': sr_levels['resistance'],
                **technical_data
            }
            
            logger.info(f"📊 Market data collected: BTC ${price:,.2f} | Vol: {ticker.get('volume', 0):,.0f}")
            
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Market data collection failed: {e}")
            return self._get_fallback_market_data()
    
    async def get_current_price(self, symbol: str = 'BTCUSDT') -> float:
        """Lấy giá hiện tại"""
        try:
            # Check cache first
            cache_key = f"price_{symbol}"
            if self._is_cache_valid(cache_key):
                return self.price_cache[cache_key]['data']
            
            url = f"{self.api_endpoints['binance']}/ticker/price"
            params = {'symbol': symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = float(data['price'])
                        
                        # Cache result
                        self.price_cache[cache_key] = {
                            'data': price,
                            'timestamp': datetime.now()
                        }
                        
                        return price
            
            # Fallback price
            return 45000.0
            
        except Exception as e:
            logger.error(f"❌ Price fetch failed: {e}")
            return 45000.0  # Fallback price
    
    async def get_24h_ticker(self, symbol: str = 'BTCUSDT') -> Dict[str, Any]:
        """Lấy thông tin ticker 24h"""
        try:
            url = f"{self.api_endpoints['binance']}/ticker/24hr"
            params = {'symbol': symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'high': float(data['highPrice']),
                            'low': float(data['lowPrice']),
                            'volume': float(data['volume']),
                            'quoteVolume': float(data['quoteVolume']),
                            'priceChange': float(data['priceChange']),
                            'priceChangePercent': float(data['priceChangePercent'])
                        }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ 24h ticker fetch failed: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str = 'BTCUSDT', limit: int = 10) -> Dict[str, Any]:
        """Lấy orderbook"""
        try:
            url = f"{self.api_endpoints['binance']}/depth"
            params = {'symbol': symbol, 'limit': limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'bids': [[float(price), float(qty)] for price, qty in data['bids']],
                            'asks': [[float(price), float(qty)] for price, qty in data['asks']]
                        }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Orderbook fetch failed: {e}")
            return {}
    
    async def get_recent_trades(self, symbol: str = 'BTCUSDT', limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy trades gần nhất"""
        try:
            url = f"{self.api_endpoints['binance']}/trades"
            params = {'symbol': symbol, 'limit': limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                'price': float(trade['price']),
                                'qty': float(trade['qty']),
                                'time': int(trade['time']),
                                'isBuyerMaker': trade['isBuyerMaker']
                            }
                            for trade in data
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Recent trades fetch failed: {e}")
            return []
    
    async def get_kline_data(self, symbol: str = 'BTCUSDT', interval: str = '1h', limit: int = 100) -> List[Dict[str, Any]]:
        """Lấy dữ liệu candlestick"""
        try:
            url = f"{self.api_endpoints['binance']}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                'timestamp': int(kline[0]),
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[5]),
                                'close_time': int(kline[6]),
                                'quote_volume': float(kline[7]),
                                'trades_count': int(kline[8])
                            }
                            for kline in data
                        ]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Kline data fetch failed: {e}")
            return []
    
    async def calculate_technical_indicators(self, klines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tính toán các chỉ báo kỹ thuật"""
        if not klines or len(klines) < 20:
            return self._get_default_indicators()
        
        try:
            closes = [k['close'] for k in klines]
            highs = [k['high'] for k in klines]
            lows = [k['low'] for k in klines]
            volumes = [k['volume'] for k in klines]
            
            indicators = {
                'rsi': self._calculate_rsi(closes),
                'macd': self._calculate_macd(closes),
                'moving_averages': self._calculate_moving_averages(closes),
                'bollinger_bands': self._calculate_bollinger_bands(closes),
                'stochastic': self._calculate_stochastic(highs, lows, closes),
                'volume_sma': self._calculate_sma(volumes, 20)
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Technical indicators calculation failed: {e}")
            return self._get_default_indicators()
    
    def calculate_support_resistance(self, klines: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Tính toán support/resistance levels"""
        if not klines:
            return {'support': [], 'resistance': []}
        
        try:
            highs = [k['high'] for k in klines[-50:]]  # Last 50 candles
            lows = [k['low'] for k in klines[-50:]]
            
            # Simple pivot point method
            support_levels = []
            resistance_levels = []
            
            for i in range(2, len(lows) - 2):
                # Local minimum (support)
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    support_levels.append(lows[i])
                
                # Local maximum (resistance)
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    resistance_levels.append(highs[i])
            
            # Sort and remove duplicates
            support_levels = sorted(list(set(support_levels)))[-5:]  # Keep last 5
            resistance_levels = sorted(list(set(resistance_levels)))[-5:]  # Keep last 5
            
            return {
                'support': support_levels,
                'resistance': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"❌ S/R calculation failed: {e}")
            return {'support': [], 'resistance': []}
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """Calculate MACD"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        
        # For signal line, we need MACD history (simplified here)
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """Calculate various moving averages"""
        return {
            'sma_20': self._calculate_sma(prices, 20),
            'sma_50': self._calculate_sma(prices, 50),
            'ema_12': self._calculate_ema(prices, 12),
            'ema_26': self._calculate_ema(prices, 26),
            'current_price': prices[-1] if prices else 0
        }
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return {'upper': current_price, 'middle': current_price, 'lower': current_price}
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        variance = sum((price - sma) ** 2 for price in recent_prices) / period
        std = variance ** 0.5
        
        return {
            'upper': sma + (std_dev * std),
            'middle': sma,
            'lower': sma - (std_dev * std)
        }
    
    def _calculate_stochastic(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Dict[str, float]:
        """Calculate Stochastic Oscillator"""
        if len(closes) < period:
            return {'k': 50, 'd': 50}
        
        recent_highs = highs[-period:]
        recent_lows = lows[-period:]
        current_close = closes[-1]
        
        highest_high = max(recent_highs)
        lowest_low = min(recent_lows)
        
        if highest_high == lowest_low:
            k = 50
        else:
            k = 100 * (current_close - lowest_low) / (highest_high - lowest_low)
        
        # Simplified %D calculation
        d = k * 0.9  # Simplified
        
        return {'k': k, 'd': d}
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        return sum(prices[-period:]) / period
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if not prices:
            return 0
        
        if len(prices) < period:
            return self._calculate_sma(prices, len(prices))
        
        multiplier = 2 / (period + 1)
        ema = self._calculate_sma(prices[:period], period)
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_spread(self, orderbook: Dict[str, Any]) -> float:
        """Calculate bid-ask spread"""
        if not orderbook.get('bids') or not orderbook.get('asks'):
            return 0
        
        best_bid = orderbook['bids'][0][0]
        best_ask = orderbook['asks'][0][0]
        
        return best_ask - best_bid
    
    def _calculate_avg_volume(self, klines: List[Dict[str, Any]], period: int = 20) -> float:
        """Calculate average volume"""
        if not klines:
            return 0
        
        volumes = [k['volume'] for k in klines[-period:]]
        return sum(volumes) / len(volumes)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.price_cache:
            return False
        
        cache_time = self.price_cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).seconds < self.cache_timeout
    
    async def _test_api_connections(self):
        """Test API connectivity"""
        try:
            url = f"{self.api_endpoints['binance']}/ping"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Binance API test failed: {response.status}")
            
            logger.info("✅ API connections tested successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ API test warning: {e}")
    
    def _get_fallback_market_data(self) -> Dict[str, Any]:
        """Fallback market data when APIs fail"""
        return {
            'symbol': 'BTCUSDT',
            'timestamp': datetime.now().isoformat(),
            'price': 45000.0,
            'volume': 1000000,
            'volume_quote': 45000000000,
            'high_24h': 46000,
            'low_24h': 44000,
            'price_change_24h': 500,
            'price_change_percent_24h': 1.12,
            'bid_price': 44995,
            'ask_price': 45005,
            'spread': 10,
            'avg_volume': 950000,
            'support_levels': [44000, 43500, 43000],
            'resistance_levels': [45500, 46000, 46500],
            **self._get_default_indicators()
        }
    
    def _get_default_indicators(self) -> Dict[str, Any]:
        """Default technical indicators"""
        return {
            'rsi': 50.0,
            'macd': {'macd': 0, 'signal': 0, 'histogram': 0},
            'moving_averages': {
                'sma_20': 45000,
                'sma_50': 44800,
                'ema_12': 45100,
                'ema_26': 44900,
                'current_price': 45000
            },
            'bollinger_bands': {'upper': 45500, 'middle': 45000, 'lower': 44500},
            'stochastic': {'k': 50, 'd': 50},
            'volume_sma': 1000000
        }
