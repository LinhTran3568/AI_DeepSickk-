"""
Signal Generator - Tạo tín hiệu giao dịch từ AI và technical analysis
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.settings import Settings

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Tạo và quản lý tín hiệu giao dịch"""
    
    def __init__(self):
        self.settings = Settings()
        self.min_confidence = self.settings.MIN_CONFIDENCE_SCORE
    
    async def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo tín hiệu từ technical analysis
        
        Args:
            market_data: Dữ liệu thị trường
            
        Returns:
            Technical signals
        """
        try:
            signals = {
                'rsi_signal': self._analyze_rsi(market_data.get('rsi', 50)),
                'macd_signal': self._analyze_macd(market_data.get('macd', {})),
                'moving_averages': self._analyze_moving_averages(market_data.get('moving_averages', {})),
                'volume_signal': self._analyze_volume(market_data.get('volume', 0), market_data.get('avg_volume', 0)),
                'support_resistance': self._analyze_support_resistance(
                    market_data.get('price', 0),
                    market_data.get('support_levels', []),
                    market_data.get('resistance_levels', [])
                )
            }
            
            # Tổng hợp tín hiệu
            combined_signal = self._combine_technical_signals(signals)
            
            logger.info(f"📊 Technical signals generated: {combined_signal['action']} - {combined_signal['confidence']:.2%}")
            
            return combined_signal
            
        except Exception as e:
            logger.error(f"❌ Signal generation failed: {e}")
            return self._get_neutral_signal()
    
    async def combine_signals(self, ai_analysis: Dict[str, Any], technical_signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kết hợp AI analysis và technical signals
        
        Args:
            ai_analysis: Kết quả phân tích AI
            technical_signals: Technical signals
            
        Returns:
            Combined signal
        """
        try:
            # Weighted combination (AI: 60%, Technical: 40%)
            ai_weight = 0.6
            tech_weight = 0.4
            
            ai_score = self._convert_action_to_score(ai_analysis.get('action', 'HOLD'))
            tech_score = self._convert_action_to_score(technical_signals.get('action', 'HOLD'))
            
            # Calculate weighted score
            combined_score = (ai_score * ai_weight) + (tech_score * tech_weight)
            
            # Convert back to action
            combined_action = self._convert_score_to_action(combined_score)
            
            # Calculate combined confidence
            ai_confidence = ai_analysis.get('confidence', 0.5)
            tech_confidence = technical_signals.get('confidence', 0.5)
            combined_confidence = (ai_confidence * ai_weight) + (tech_confidence * tech_weight)
            
            # Create combined signal
            combined_signal = {
                'action': combined_action,
                'confidence': combined_confidence,
                'entry_price': ai_analysis.get('entry_price', 0),
                'stop_loss': ai_analysis.get('stop_loss', 0),
                'take_profit': ai_analysis.get('take_profit', 0),
                'risk_level': ai_analysis.get('risk_level', 'MEDIUM'),
                'timeframe': ai_analysis.get('timeframe', '1h'),
                'reasoning': f"AI: {ai_analysis.get('reasoning', 'N/A')} | Tech: {technical_signals.get('reasoning', 'N/A')}",
                'ai_component': {
                    'action': ai_analysis.get('action'),
                    'confidence': ai_confidence,
                    'sentiment': ai_analysis.get('market_sentiment', 'NEUTRAL')
                },
                'technical_component': {
                    'action': technical_signals.get('action'),
                    'confidence': tech_confidence,
                    'key_indicators': technical_signals.get('key_indicators', [])
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Validate signal
            if combined_confidence < self.min_confidence:
                combined_signal['action'] = 'HOLD'
                combined_signal['reasoning'] += f" | Confidence too low: {combined_confidence:.2%}"
            
            logger.info(f"🎯 Combined signal: {combined_action} - {combined_confidence:.2%}")
            
            return combined_signal
            
        except Exception as e:
            logger.error(f"❌ Signal combination failed: {e}")
            return self._get_neutral_signal()
    
    def _analyze_rsi(self, rsi: float) -> Dict[str, Any]:
        """Phân tích RSI indicator"""
        if rsi <= self.settings.RSI_OVERSOLD:
            return {
                'action': 'BUY',
                'strength': 'STRONG' if rsi <= 20 else 'MEDIUM',
                'value': rsi,
                'reason': f'RSI oversold at {rsi:.1f}'
            }
        elif rsi >= self.settings.RSI_OVERBOUGHT:
            return {
                'action': 'SELL',
                'strength': 'STRONG' if rsi >= 80 else 'MEDIUM',
                'value': rsi,
                'reason': f'RSI overbought at {rsi:.1f}'
            }
        else:
            return {
                'action': 'HOLD',
                'strength': 'WEAK',
                'value': rsi,
                'reason': f'RSI neutral at {rsi:.1f}'
            }
    
    def _analyze_macd(self, macd_data: Dict[str, float]) -> Dict[str, Any]:
        """Phân tích MACD indicator"""
        macd_line = macd_data.get('macd', 0)
        signal_line = macd_data.get('signal', 0)
        histogram = macd_data.get('histogram', 0)
        
        if macd_line > signal_line and histogram > 0:
            return {
                'action': 'BUY',
                'strength': 'MEDIUM',
                'values': macd_data,
                'reason': 'MACD bullish crossover'
            }
        elif macd_line < signal_line and histogram < 0:
            return {
                'action': 'SELL',
                'strength': 'MEDIUM',
                'values': macd_data,
                'reason': 'MACD bearish crossover'
            }
        else:
            return {
                'action': 'HOLD',
                'strength': 'WEAK',
                'values': macd_data,
                'reason': 'MACD no clear signal'
            }
    
    def _analyze_moving_averages(self, ma_data: Dict[str, float]) -> Dict[str, Any]:
        """Phân tích Moving Averages"""
        sma_20 = ma_data.get('sma_20', 0)
        sma_50 = ma_data.get('sma_50', 0)
        ema_12 = ma_data.get('ema_12', 0)
        ema_26 = ma_data.get('ema_26', 0)
        current_price = ma_data.get('current_price', 0)
        
        signals = []
        
        # Price vs SMA
        if current_price > sma_20 > sma_50:
            signals.append('bullish_ma_trend')
        elif current_price < sma_20 < sma_50:
            signals.append('bearish_ma_trend')
        
        # EMA crossover
        if ema_12 > ema_26:
            signals.append('bullish_ema_cross')
        elif ema_12 < ema_26:
            signals.append('bearish_ema_cross')
        
        # Determine overall MA signal
        bullish_signals = sum(1 for s in signals if 'bullish' in s)
        bearish_signals = sum(1 for s in signals if 'bearish' in s)
        
        if bullish_signals > bearish_signals:
            action = 'BUY'
        elif bearish_signals > bullish_signals:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'strength': 'MEDIUM',
            'signals': signals,
            'reason': f'MA analysis: {len(signals)} signals detected'
        }
    
    def _analyze_volume(self, current_volume: float, avg_volume: float) -> Dict[str, Any]:
        """Phân tích Volume"""
        if avg_volume == 0:
            return {'action': 'HOLD', 'strength': 'WEAK', 'reason': 'No volume data'}
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5:  # High volume
            return {
                'action': 'CONFIRM',  # Volume confirms other signals
                'strength': 'STRONG',
                'ratio': volume_ratio,
                'reason': f'High volume: {volume_ratio:.1f}x average'
            }
        elif volume_ratio < 0.5:  # Low volume
            return {
                'action': 'CAUTION',
                'strength': 'WEAK',
                'ratio': volume_ratio,
                'reason': f'Low volume: {volume_ratio:.1f}x average'
            }
        else:
            return {
                'action': 'HOLD',
                'strength': 'MEDIUM',
                'ratio': volume_ratio,
                'reason': 'Normal volume'
            }
    
    def _analyze_support_resistance(self, current_price: float, support_levels: List[float], 
                                  resistance_levels: List[float]) -> Dict[str, Any]:
        """Phân tích Support/Resistance levels"""
        if not support_levels and not resistance_levels:
            return {'action': 'HOLD', 'reason': 'No S/R levels'}
        
        # Check proximity to support/resistance
        nearest_support = max([s for s in support_levels if s < current_price], default=0)
        nearest_resistance = min([r for r in resistance_levels if r > current_price], default=float('inf'))
        
        support_distance = (current_price - nearest_support) / current_price if nearest_support > 0 else 1
        resistance_distance = (nearest_resistance - current_price) / current_price if nearest_resistance < float('inf') else 1
        
        if support_distance < 0.02:  # Within 2% of support
            return {
                'action': 'BUY',
                'strength': 'MEDIUM',
                'level': nearest_support,
                'reason': f'Near support at ${nearest_support:.2f}'
            }
        elif resistance_distance < 0.02:  # Within 2% of resistance
            return {
                'action': 'SELL',
                'strength': 'MEDIUM',
                'level': nearest_resistance,
                'reason': f'Near resistance at ${nearest_resistance:.2f}'
            }
        else:
            return {
                'action': 'HOLD',
                'strength': 'WEAK',
                'reason': 'Not near significant S/R levels'
            }
    
    def _combine_technical_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Tổng hợp các technical signals"""
        # Weight các indicators
        weights = {
            'rsi_signal': 0.25,
            'macd_signal': 0.25,
            'moving_averages': 0.25,
            'support_resistance': 0.20,
            'volume_signal': 0.05
        }
        
        total_score = 0
        total_weight = 0
        key_indicators = []
        reasoning_parts = []
        
        for signal_name, signal_data in signals.items():
            if signal_name in weights:
                action = signal_data.get('action', 'HOLD')
                weight = weights[signal_name]
                
                # Skip volume signal for scoring (it's confirmation only)
                if action not in ['CONFIRM', 'CAUTION']:
                    score = self._convert_action_to_score(action)
                    total_score += score * weight
                    total_weight += weight
                    
                    if action != 'HOLD':
                        key_indicators.append(f"{signal_name}: {action}")
                        reasoning_parts.append(signal_data.get('reason', ''))
        
        # Calculate final action and confidence
        if total_weight > 0:
            avg_score = total_score / total_weight
            final_action = self._convert_score_to_action(avg_score)
            confidence = min(abs(avg_score - 0.5) * 2, 1.0)  # Distance from neutral
        else:
            final_action = 'HOLD'
            confidence = 0.5
        
        return {
            'action': final_action,
            'confidence': confidence,
            'key_indicators': key_indicators,
            'reasoning': '; '.join(reasoning_parts) if reasoning_parts else 'No strong technical signals',
            'signal_scores': {k: v.get('action') for k, v in signals.items()}
        }
    
    def _convert_action_to_score(self, action: str) -> float:
        """Convert action to numerical score"""
        action_map = {
            'BUY': 1.0,
            'SELL': 0.0,
            'HOLD': 0.5
        }
        return action_map.get(action, 0.5)
    
    def _convert_score_to_action(self, score: float) -> str:
        """Convert numerical score to action"""
        if score > 0.6:
            return 'BUY'
        elif score < 0.4:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _get_neutral_signal(self) -> Dict[str, Any]:
        """Return neutral signal when analysis fails"""
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'risk_level': 'MEDIUM',
            'timeframe': '1h',
            'reasoning': 'Signal generation failed, defaulting to HOLD',
            'timestamp': datetime.now().isoformat()
        }
