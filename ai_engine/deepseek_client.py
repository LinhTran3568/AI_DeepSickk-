"""
DeepSeek API Client cho Bitcoin Trading Analysis
"""
import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.settings import Settings

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Client để giao tiếp với DeepSeek API"""
    
    def __init__(self):
        self.settings = Settings()
        self.api_key = self.settings.DEEPSEEK_API_KEY
        self.base_url = self.settings.DEEPSEEK_API_BASE
        self.model = self.settings.DEEPSEEK_MODEL
        self.max_tokens = self.settings.DEEPSEEK_MAX_TOKENS
    
    async def test_connection(self) -> bool:
        """Test kết nối với DeepSeek API"""
        try:
            # Check if API key is configured
            if not self.api_key or self.api_key == "your_valid_deepseek_api_key_here":
                logger.warning("⚠️ DeepSeek API key not configured - using fallback mode")
                return False
                
            test_prompt = "Hello, this is a connection test."
            response = await self._make_request(test_prompt)
            
            if response and 'choices' in response:
                logger.info("✅ DeepSeek API connection successful")
                return True
            else:
                logger.error("❌ DeepSeek API connection failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API test failed: {e}")
            return False
    
    async def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân tích thị trường Bitcoin với AI
        
        Args:
            market_data: Dữ liệu thị trường
            
        Returns:
            Kết quả phân tích AI
        """
        try:
            # Check if API is available
            if not self.api_key or self.api_key == "your_valid_deepseek_api_key_here":
                logger.info("🤖 Using fallback AI analysis (DeepSeek API not configured)")
                return self._get_fallback_analysis(market_data)
            
            # Tạo prompt phân tích chuyên sâu
            prompt = self._create_market_analysis_prompt(market_data)
            
            # Gọi DeepSeek API
            response = await self._make_request(prompt)
            
            # Parse kết quả
            analysis = self._parse_analysis_response(response)
            
            logger.info(f"🧠 AI Analysis completed: {analysis.get('action')} with {analysis.get('confidence'):.2%} confidence")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Market analysis failed: {e}")
            return self._get_fallback_analysis(market_data)
    
    async def analyze_pattern(self, price_data: List[float], timeframe: str) -> Dict[str, Any]:
        """
        Phân tích pattern biểu đồ
        
        Args:
            price_data: Dữ liệu giá
            timeframe: Khung thời gian
            
        Returns:
            Kết quả phân tích pattern
        """
        try:
            prompt = self._create_pattern_analysis_prompt(price_data, timeframe)
            response = await self._make_request(prompt)
            
            return self._parse_pattern_response(response)
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {e}")
            return {"pattern": "unknown", "confidence": 0.5}
    
    async def predict_trend(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dự đoán xu hướng ngắn hạn
        
        Args:
            historical_data: Dữ liệu lịch sử
            
        Returns:
            Dự đoán xu hướng
        """
        try:
            prompt = self._create_trend_prediction_prompt(historical_data)
            response = await self._make_request(prompt)
            
            return self._parse_trend_response(response)
            
        except Exception as e:
            logger.error(f"❌ Trend prediction failed: {e}")
            return {"trend": "neutral", "confidence": 0.5, "timeframe": "1h"}
    
    def _create_market_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """Tạo prompt phân tích thị trường"""
        current_price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)
        rsi = market_data.get('rsi', 50)
        macd = market_data.get('macd', {})
        support_levels = market_data.get('support_levels', [])
        resistance_levels = market_data.get('resistance_levels', [])
        
        prompt = f"""
Bạn là một chuyên gia phân tích Bitcoin trading với kinh nghiệm 10+ năm. 
Hãy phân tích dữ liệu thị trường sau và đưa ra quyết định giao dịch:

THÔNG TIN THỊ TRƯỜNG:
- Giá hiện tại: ${current_price:,.2f}
- Volume 24h: {volume:,.0f}
- RSI: {rsi:.2f}
- MACD: {macd}
- Support levels: {support_levels}
- Resistance levels: {resistance_levels}

YÊU CẦU PHÂN TÍCH:
1. Phân tích xu hướng ngắn hạn (1-4h)
2. Đánh giá mức độ rủi ro hiện tại
3. Xác định điểm vào lệnh tối ưu
4. Đề xuất stop loss và take profit
5. Tính confidence score (0-1)

ĐỊNH DẠNG TRẢ LỜI (JSON):
{{
    "action": "BUY/SELL/HOLD",
    "confidence": 0.85,
    "entry_price": 45000,
    "stop_loss": 44100,
    "take_profit": 46800,
    "risk_level": "LOW/MEDIUM/HIGH",
    "timeframe": "1h",
    "reasoning": "Lý do chi tiết cho quyết định",
    "key_factors": ["factor1", "factor2", "factor3"],
    "market_sentiment": "BULLISH/BEARISH/NEUTRAL"
}}

Chỉ trả lời bằng JSON, không thêm text khác.
"""
        return prompt
    
    def _create_pattern_analysis_prompt(self, price_data: List[float], timeframe: str) -> str:
        """Tạo prompt phân tích pattern"""
        recent_prices = price_data[-20:] if len(price_data) > 20 else price_data
        
        prompt = f"""
Phân tích pattern biểu đồ Bitcoin sau đây (timeframe {timeframe}):

Dữ liệu giá gần nhất (20 periods): {recent_prices}

Xác định:
1. Pattern chính (Head & Shoulders, Triangle, Flag, etc.)
2. Độ tin cậy của pattern
3. Hướng breakout có thể xảy ra
4. Target price nếu breakout

Trả lời JSON format:
{{
    "pattern": "pattern_name",
    "confidence": 0.8,
    "breakout_direction": "UP/DOWN",
    "target_price": 46000,
    "pattern_completion": 0.7
}}
"""
        return prompt
    
    def _create_trend_prediction_prompt(self, historical_data: Dict[str, Any]) -> str:
        """Tạo prompt dự đoán xu hướng"""
        prompt = f"""
Dựa trên dữ liệu lịch sử Bitcoin sau, dự đoán xu hướng ngắn hạn:

{json.dumps(historical_data, indent=2)}

Phân tích và dự đoán:
1. Xu hướng trong 1-4 giờ tới
2. Các level price quan trọng
3. Xác suất thành công

JSON format:
{{
    "trend": "BULLISH/BEARISH/NEUTRAL",
    "confidence": 0.75,
    "timeframe": "4h",
    "target_levels": [45000, 46000, 47000],
    "probability": 0.8
}}
"""
        return prompt
    
    async def _make_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Gửi request đến DeepSeek API via OpenRouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/bitcoin-trading-bot",
                "X-Title": "Bitcoin Trading Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.1,  # Low temperature for consistent analysis
                "stream": False
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ DeepSeek API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ DeepSeek request failed: {e}")
            return None
    
    def _parse_analysis_response(self, response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse phản hồi phân tích từ AI"""
        if not response or 'choices' not in response:
            return self._get_default_analysis()
        
        try:
            content = response['choices'][0]['message']['content']
            
            # Tìm JSON trong response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['action', 'confidence', 'entry_price']
                if all(field in analysis for field in required_fields):
                    return analysis
            
            logger.warning("⚠️ Invalid AI response format, using default")
            return self._get_default_analysis()
            
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            return self._get_default_analysis()
    
    def _parse_pattern_response(self, response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse phản hồi pattern analysis"""
        if not response:
            return {"pattern": "unknown", "confidence": 0.5}
        
        try:
            content = response['choices'][0]['message']['content']
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"❌ Error parsing pattern response: {e}")
        
        return {"pattern": "unknown", "confidence": 0.5}
    
    def _parse_trend_response(self, response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse phản hồi trend prediction"""
        if not response:
            return {"trend": "neutral", "confidence": 0.5}
        
        try:
            content = response['choices'][0]['message']['content']
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"❌ Error parsing trend response: {e}")
        
        return {"trend": "neutral", "confidence": 0.5}
    
    def _get_fallback_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback AI analysis dựa trên rule-based logic"""
        try:
            current_price = market_data.get('price', 45000)
            rsi = market_data.get('rsi', 50)
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', 1000000)
            
            # Simple rule-based analysis
            action = "HOLD"
            confidence = 0.6
            reasoning = "Fallback analysis: "
            
            # RSI-based signals
            if rsi < 30:
                action = "BUY"
                confidence += 0.2
                reasoning += "RSI oversold, "
            elif rsi > 70:
                action = "SELL"  
                confidence += 0.2
                reasoning += "RSI overbought, "
            
            # Volume confirmation
            if volume > avg_volume * 1.5:
                confidence += 0.1
                reasoning += "high volume confirmation, "
            
            # Price level analysis
            support_levels = market_data.get('support_levels', [])
            resistance_levels = market_data.get('resistance_levels', [])
            
            if support_levels:
                nearest_support = max([s for s in support_levels if s < current_price], default=0)
                if nearest_support > 0 and (current_price - nearest_support) / current_price < 0.02:
                    action = "BUY" if action != "SELL" else action
                    confidence += 0.1
                    reasoning += "near support level, "
            
            if resistance_levels:
                nearest_resistance = min([r for r in resistance_levels if r > current_price], default=float('inf'))
                if nearest_resistance < float('inf') and (nearest_resistance - current_price) / current_price < 0.02:
                    action = "SELL" if action != "BUY" else action
                    confidence += 0.1
                    reasoning += "near resistance level, "
            
            # Cap confidence
            confidence = min(confidence, 0.85)
            
            return {
                "action": action,
                "confidence": confidence,
                "entry_price": current_price,
                "stop_loss": current_price * 0.98 if action == "BUY" else current_price * 1.02,
                "take_profit": current_price * 1.04 if action == "BUY" else current_price * 0.96,
                "risk_level": "MEDIUM",
                "timeframe": "1h",
                "reasoning": reasoning.rstrip(", "),
                "key_factors": ["rule_based_analysis", "technical_indicators"],
                "market_sentiment": "NEUTRAL"
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback analysis failed: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Trả về phân tích mặc định khi AI thất bại"""
        return {
            "action": "HOLD",
            "confidence": 0.5,
            "entry_price": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "risk_level": "MEDIUM",
            "timeframe": "1h",
            "reasoning": "AI analysis unavailable, default to HOLD",
            "key_factors": ["ai_unavailable"],
            "market_sentiment": "NEUTRAL"
        }
