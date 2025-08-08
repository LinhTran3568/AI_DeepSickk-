"""
Continuous AI Analysis Engine - Đánh giá và lập kế hoạch liên tục
"""
import time
import threading
from datetime import datetime, timedelta
import random
import json

class ContinuousAIAnalyzer:
    def __init__(self):
        self.analysis_interval = 10  # Phân tích mỗi 10 giây
        self.plan_update_interval = 60  # Cập nhật kế hoạch mỗi 60 giây
        self.running = False
        self.current_analysis = {}
        self.current_plans = {}
        self.market_sentiment = "neutral"
        self.confidence_trend = []
        self.analysis_history = []
        
        # Real-time market indicators
        self.indicators = {
            'price_momentum': 0.0,
            'volume_trend': 1.0,
            'volatility': 0.05,
            'market_pressure': 0.0,
            'news_sentiment': 0.0
        }
        
        # Strategy templates
        self.strategies = {
            'aggressive': {
                'risk_tolerance': 0.05,
                'hold_time_multiplier': 0.7,
                'profit_target_multiplier': 1.5,
                'frequency': 'high'
            },
            'conservative': {
                'risk_tolerance': 0.02,
                'hold_time_multiplier': 1.5,
                'profit_target_multiplier': 0.8,
                'frequency': 'low'
            },
            'balanced': {
                'risk_tolerance': 0.03,
                'hold_time_multiplier': 1.0,
                'profit_target_multiplier': 1.0,
                'frequency': 'medium'
            }
        }
        
    def start_continuous_analysis(self):
        """Bắt đầu phân tích liên tục"""
        self.running = True
        
        # Thread cho phân tích real-time
        analysis_thread = threading.Thread(target=self._continuous_analysis_loop, daemon=True)
        analysis_thread.start()
        
        # Thread cho cập nhật kế hoạch
        planning_thread = threading.Thread(target=self._continuous_planning_loop, daemon=True)
        planning_thread.start()
        
        print("🧠 AI Continuous Analyzer started")
        
    def stop_continuous_analysis(self):
        """Dừng phân tích liên tục"""
        self.running = False
        print("🛑 AI Continuous Analyzer stopped")
        
    def _continuous_analysis_loop(self):
        """Vòng lặp phân tích liên tục"""
        while self.running:
            try:
                # Cập nhật chỉ số thị trường
                self._update_market_indicators()
                
                # Thực hiện phân tích
                analysis = self._perform_real_time_analysis()
                
                # Lưu kết quả
                self.current_analysis = analysis
                self.analysis_history.append({
                    'timestamp': datetime.now(),
                    'analysis': analysis
                })
                
                # Giữ lại 100 phân tích gần nhất
                if len(self.analysis_history) > 100:
                    self.analysis_history = self.analysis_history[-100:]
                    
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                print(f"❌ Analysis error: {e}")
                time.sleep(5)
                
    def _continuous_planning_loop(self):
        """Vòng lặp lập kế hoạch liên tục"""
        while self.running:
            try:
                # Tạo kế hoạch mới dựa trên phân tích hiện tại
                plans = self._generate_updated_plans()
                self.current_plans = plans
                
                time.sleep(self.plan_update_interval)
                
            except Exception as e:
                print(f"❌ Planning error: {e}")
                time.sleep(10)
                
    def _update_market_indicators(self):
        """Cập nhật các chỉ số thị trường real-time"""
        # Simulate real market data updates
        self.indicators['price_momentum'] += random.uniform(-0.01, 0.01)
        self.indicators['price_momentum'] = max(-0.1, min(0.1, self.indicators['price_momentum']))
        
        self.indicators['volume_trend'] *= random.uniform(0.95, 1.05)
        self.indicators['volume_trend'] = max(0.5, min(2.0, self.indicators['volume_trend']))
        
        self.indicators['volatility'] = random.uniform(0.02, 0.08)
        
        # Market pressure (buying vs selling pressure)
        self.indicators['market_pressure'] += random.uniform(-0.02, 0.02)
        self.indicators['market_pressure'] = max(-0.2, min(0.2, self.indicators['market_pressure']))
        
        # News sentiment simulation
        self.indicators['news_sentiment'] = random.uniform(-0.1, 0.1)
        
    def _perform_real_time_analysis(self):
        """Thực hiện phân tích real-time"""
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        
        # Tính toán signal strength từ nhiều yếu tố
        signal_strength = 0.5  # Base strength
        
        # Price momentum influence
        signal_strength += self.indicators['price_momentum'] * 3
        
        # Volume influence
        if self.indicators['volume_trend'] > 1.2:
            signal_strength += 0.1
        elif self.indicators['volume_trend'] < 0.8:
            signal_strength -= 0.1
            
        # Market pressure influence
        signal_strength += self.indicators['market_pressure'] * 2
        
        # Volatility influence (high volatility = more opportunities)
        if self.indicators['volatility'] > 0.06:
            signal_strength += 0.05
            
        # News sentiment influence
        signal_strength += self.indicators['news_sentiment'] * 1.5
        
        # Time-based patterns
        time_patterns = {
            (9, 11): 0.1,   # Morning bullish
            (11, 14): -0.05, # Lunch neutral
            (14, 16): 0.05,  # Afternoon slightly bullish
            (16, 18): 0.0,   # Late afternoon neutral
            (20, 22): -0.1,  # Evening bearish
        }
        
        for (start_hour, end_hour), pattern_strength in time_patterns.items():
            if start_hour <= hour < end_hour:
                signal_strength += pattern_strength
                break
                
        # Normalize signal strength
        signal_strength = max(0.1, min(0.9, signal_strength))
        
        # Determine action and confidence
        if signal_strength > 0.65:
            action = "BUY"
            confidence = signal_strength
            recommendation = "Tín hiệu mua mạnh"
        elif signal_strength < 0.35:
            action = "SELL"
            confidence = 1 - signal_strength
            recommendation = "Tín hiệu bán mạnh"
        else:
            action = "HOLD"
            confidence = 0.6 + random.uniform(-0.1, 0.1)
            recommendation = "Chờ tín hiệu rõ ràng"
            
        # Generate detailed analysis
        analysis_details = self._generate_analysis_details(action, signal_strength)
        
        # Update confidence trend
        self.confidence_trend.append(confidence)
        if len(self.confidence_trend) > 20:
            self.confidence_trend = self.confidence_trend[-20:]
            
        return {
            'timestamp': current_time,
            'action': action,
            'confidence': confidence,
            'signal_strength': signal_strength,
            'recommendation': recommendation,
            'details': analysis_details,
            'market_session': self._get_market_session(hour),
            'indicators': self.indicators.copy(),
            'trend_direction': self._calculate_trend_direction(),
            'risk_level': self._calculate_risk_level(),
            'optimal_timeframe': self._suggest_optimal_timeframe(signal_strength)
        }
        
    def _generate_analysis_details(self, action, signal_strength):
        """Tạo chi tiết phân tích"""
        details = []
        
        # Price momentum analysis
        momentum = self.indicators['price_momentum']
        if momentum > 0.03:
            details.append("💹 Momentum tăng mạnh (+{:.1%})".format(momentum))
        elif momentum < -0.03:
            details.append("📉 Momentum giảm mạnh ({:.1%})".format(momentum))
        else:
            details.append("📊 Momentum ổn định ({:.1%})".format(momentum))
            
        # Volume analysis
        volume = self.indicators['volume_trend']
        if volume > 1.3:
            details.append("🔊 Volume rất cao ({:.1f}x)".format(volume))
        elif volume > 1.1:
            details.append("📈 Volume cao ({:.1f}x)".format(volume))
        elif volume < 0.8:
            details.append("📉 Volume thấp ({:.1f}x)".format(volume))
        else:
            details.append("📊 Volume bình thường ({:.1f}x)".format(volume))
            
        # Market pressure analysis
        pressure = self.indicators['market_pressure']
        if pressure > 0.1:
            details.append("🟢 Áp lực mua mạnh (+{:.1%})".format(pressure))
        elif pressure < -0.1:
            details.append("🔴 Áp lực bán mạnh ({:.1%})".format(pressure))
        else:
            details.append("⚖️ Áp lực cân bằng ({:.1%})".format(pressure))
            
        # Volatility analysis
        volatility = self.indicators['volatility']
        if volatility > 0.06:
            details.append("⚡ Volatility cao ({:.1%}) - Cơ hội trading".format(volatility))
        else:
            details.append("😴 Volatility thấp ({:.1%}) - Thị trường yên tĩnh".format(volatility))
            
        return details
        
    def _get_market_session(self, hour):
        """Xác định phiên giao dịch"""
        if 9 <= hour < 11:
            return "morning_breakout"
        elif 11 <= hour < 14:
            return "lunch_consolidation"
        elif 14 <= hour < 18:
            return "afternoon_momentum"
        elif 18 <= hour < 22:
            return "evening_session"
        else:
            return "night_session"
            
    def _calculate_trend_direction(self):
        """Tính hướng xu hướng"""
        if len(self.confidence_trend) < 5:
            return "unknown"
            
        recent_trend = self.confidence_trend[-5:]
        if all(recent_trend[i] <= recent_trend[i+1] for i in range(len(recent_trend)-1)):
            return "strongly_up"
        elif all(recent_trend[i] >= recent_trend[i+1] for i in range(len(recent_trend)-1)):
            return "strongly_down"
        elif recent_trend[-1] > recent_trend[0]:
            return "up"
        elif recent_trend[-1] < recent_trend[0]:
            return "down"
        else:
            return "sideways"
            
    def _calculate_risk_level(self):
        """Tính mức độ rủi ro"""
        volatility = self.indicators['volatility']
        if volatility > 0.07:
            return "high"
        elif volatility > 0.04:
            return "medium"
        else:
            return "low"
            
    def _suggest_optimal_timeframe(self, signal_strength):
        """Đề xuất khung thời gian tối ưu"""
        volatility = self.indicators['volatility']
        
        if volatility > 0.06 and signal_strength > 0.7:
            return "5m"  # High volatility, strong signal = scalping
        elif 0.4 < signal_strength < 0.7:
            return "15m"  # Medium signal = day trading
        elif signal_strength > 0.6:
            return "1h"   # Strong signal = swing trading
        else:
            return "4h"   # Weak signal = position trading
            
    def _generate_updated_plans(self):
        """Tạo kế hoạch cập nhật"""
        if not self.current_analysis:
            return {}
            
        analysis = self.current_analysis
        current_price = 116727.62  # Example price
        
        plans = {}
        timeframes = ['5m', '15m', '1h', '4h']
        
        for tf in timeframes:
            strategy_type = self._determine_strategy_type(analysis, tf)
            strategy = self.strategies[strategy_type]
            
            # Calculate timing based on analysis
            base_time = {'5m': 5, '15m': 15, '1h': 60, '4h': 240}[tf]
            
            # Adjust timing based on signal strength and volatility
            timing_multiplier = strategy['hold_time_multiplier']
            if analysis['signal_strength'] > 0.7:
                timing_multiplier *= 0.8  # Strong signals act faster
            elif analysis['signal_strength'] < 0.4:
                timing_multiplier *= 1.3  # Weak signals wait longer
                
            estimated_time = int(base_time * timing_multiplier)
            
            # Calculate targets
            risk_percent = strategy['risk_tolerance'] * 100
            profit_percent = risk_percent * 2 * strategy['profit_target_multiplier']
            
            if analysis['action'] == 'BUY':
                stop_loss = current_price * (1 - strategy['risk_tolerance'])
                take_profit = current_price * (1 + profit_percent/100)
                action_plan = f"Mua → Giữ {estimated_time} phút → TP ${take_profit:.0f}"
            elif analysis['action'] == 'SELL':
                stop_loss = current_price * (1 + strategy['risk_tolerance'])
                take_profit = current_price * (1 - profit_percent/100)
                action_plan = f"Bán → Giữ {estimated_time} phút → TP ${take_profit:.0f}"
            else:
                stop_loss = current_price * 0.98
                take_profit = current_price * 1.02
                action_plan = f"Hold → Đánh giá lại sau {estimated_time} phút"
                
            plans[tf] = {
                'action': analysis['action'],
                'estimated_time': estimated_time,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'action_plan': action_plan,
                'strategy_type': strategy_type,
                'confidence': analysis['confidence'],
                'risk_level': analysis['risk_level'],
                'recommendation': analysis['recommendation']
            }
            
        return plans
        
    def _determine_strategy_type(self, analysis, timeframe):
        """Xác định loại strategy phù hợp"""
        signal_strength = analysis['signal_strength']
        risk_level = analysis['risk_level']
        
        if timeframe == '5m':
            return 'aggressive' if signal_strength > 0.7 else 'balanced'
        elif timeframe in ['15m', '1h']:
            if risk_level == 'high':
                return 'conservative'
            elif signal_strength > 0.6:
                return 'balanced'
            else:
                return 'conservative'
        else:  # 4h
            return 'conservative'
            
    def get_current_analysis(self):
        """Lấy phân tích hiện tại"""
        return self.current_analysis
        
    def get_current_plans(self):
        """Lấy kế hoạch hiện tại"""
        return self.current_plans
        
    def get_analysis_summary(self):
        """Lấy tóm tắt phân tích cho dashboard"""
        if not self.current_analysis:
            return {}
            
        analysis = self.current_analysis
        plans = self.current_plans
        
        # Get best plan
        best_timeframe = analysis.get('optimal_timeframe', '15m')
        best_plan = plans.get(best_timeframe, {})
        # Cập nhật socketio trong simple_dashboard
        if hasattr(self, 'socketio') and self.socketio:
            # Emit continuous analysis
            self.socketio.emit('continuous_analysis', analysis)
            
            # Emit strategy plans
            self.socketio.emit('strategy_plans', {
                'plans_by_timeframe': {tf: plan.get('action_plan', '') for tf, plan in plans.items()},
                'best_timeframe': best_timeframe,
                'best_plan': best_plan.get('action_plan', ''),
                'confidence': f"{analysis['confidence']*100:.0f}%",
                'estimated_time': best_plan.get('estimated_time', 15)
            })
            
            # Generate and emit trading signals
            trading_signal = self._generate_trading_signal(analysis, best_plan)
            self.socketio.emit('trading_signal', trading_signal)
        
        return {
            'current_action': analysis['action'],
            'confidence': f"{analysis['confidence']*100:.0f}%",
            'trend_direction': analysis.get('trend_direction', 'unknown'),
            'risk_level': analysis.get('risk_level', 'medium'),
            'market_session': analysis.get('market_session', 'unknown'),
            'recommendation': analysis.get('recommendation', ''),
            'best_timeframe': best_timeframe,
            'best_plan': best_plan.get('action_plan', ''),
            'estimated_time': best_plan.get('estimated_time', 15),
            'analysis_details': analysis.get('details', []),
            'last_update': analysis.get('timestamp', datetime.now()).strftime('%H:%M:%S'),
            'plans_by_timeframe': {tf: plan.get('action_plan', '') for tf, plan in plans.items()}
        }

    def _generate_trading_signal(self, analysis, best_plan):
        """Tạo tín hiệu trading rõ ràng"""
        action = analysis.get('action', 'HOLD').upper()
        confidence = analysis.get('confidence', 0.75) * 100
        current_price = 116727 + random.uniform(-500, 500)  # Giá Bitcoin mô phỏng
        
        instructions = []
        
        if action == 'BUY':
            take_profit = current_price * 1.015  # +1.5%
            stop_loss = current_price * 0.985    # -1.5%
            instructions = [
                f"🎯 Take Profit: ${take_profit:,.0f} (+1.5%)",
                f"🛑 Stop Loss: ${stop_loss:,.0f} (-1.5%)",
                f"⏰ Thời gian dự kiến: {best_plan.get('estimated_time', 15)} phút",
                f"📊 Tín hiệu mạnh - Nên mua ngay"
            ]
        elif action == 'SELL':
            take_profit = current_price * 0.985  # -1.5%
            stop_loss = current_price * 1.015    # +1.5%
            instructions = [
                f"🎯 Take Profit: ${take_profit:,.0f} (-1.5%)",
                f"🛑 Stop Loss: ${stop_loss:,.0f} (+1.5%)",
                f"⏰ Thời gian dự kiến: {best_plan.get('estimated_time', 15)} phút",
                f"📊 Tín hiệu bán - Nên bán ngay"
            ]
        else:  # HOLD
            instructions = [
                f"⏰ Chờ tín hiệu tốt hơn",
                f"📊 Thị trường đang sideway",
                f"🎯 Giá mục tiêu: Chờ breakout",
                f"💡 Kiên nhẫn chờ cơ hội tốt"
            ]
        
        return {
            'action': action,
            'confidence': int(confidence),
            'current_price': current_price,
            'instructions': instructions,
            'timestamp': datetime.now().isoformat(),
            'timeframe': best_plan.get('timeframe', '15m')
        }

    def set_socketio(self, socketio):
        """Thiết lập socketio để emit data"""
        self.socketio = socketio

# Global continuous analyzer instance
continuous_analyzer = ContinuousAIAnalyzer()
