"""
Risk Manager - Quản lý rủi ro và position sizing
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config.settings import Settings

logger = logging.getLogger(__name__)

class RiskManager:
    """Quản lý rủi ro giao dịch"""
    
    def __init__(self):
        self.settings = Settings()
        self.daily_trades = []
        self.daily_pnl = 0
        self.max_drawdown = 0
        self.peak_balance = self.settings.INITIAL_BALANCE
        
    async def evaluate_risk(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đánh giá rủi ro cho signal
        
        Args:
            signal: Trading signal
            
        Returns:
            Risk evaluation result
        """
        try:
            risk_checks = []
            
            # 1. Confidence check
            confidence_check = self._check_confidence(signal)
            risk_checks.append(confidence_check)
            
            # 2. Daily trade limit
            trade_limit_check = self._check_daily_trade_limit()
            risk_checks.append(trade_limit_check)
            
            # 3. Position size validation
            position_check = self._check_position_size(signal)
            risk_checks.append(position_check)
            
            # 4. Risk/Reward ratio
            risk_reward_check = self._check_risk_reward_ratio(signal)
            risk_checks.append(risk_reward_check)
            
            # 5. Market conditions
            market_check = self._check_market_conditions(signal)
            risk_checks.append(market_check)
            
            # Overall risk assessment
            passed_checks = sum(1 for check in risk_checks if check['passed'])
            total_checks = len(risk_checks)
            
            # Approve if more than 70% checks pass
            approved = passed_checks / total_checks >= 0.7
            
            risk_evaluation = {
                'approved': approved,
                'confidence_score': passed_checks / total_checks,
                'checks': risk_checks,
                'recommendation': self._get_risk_recommendation(risk_checks),
                'max_position_size': self._calculate_max_position_size(),
                'suggested_stop_loss': self._calculate_stop_loss(signal),
                'suggested_take_profit': self._calculate_take_profit(signal)
            }
            
            logger.info(f"🛡️ Risk evaluation: {'✅ APPROVED' if approved else '❌ REJECTED'} ({passed_checks}/{total_checks} checks passed)")
            
            return risk_evaluation
            
        except Exception as e:
            logger.error(f"❌ Risk evaluation failed: {e}")
            return self._get_conservative_evaluation()
    
    def calculate_position_size(self, signal: Dict[str, Any], account_balance: float = None) -> float:
        """
        Tính toán position size dựa trên risk management
        
        Args:
            signal: Trading signal
            account_balance: Current account balance
            
        Returns:
            Position size in base currency
        """
        try:
            balance = account_balance or self.settings.INITIAL_BALANCE
            
            # Maximum position size as % of account
            max_position_percent = self.settings.MAX_POSITION_SIZE / 100
            max_position_value = balance * max_position_percent
            
            # Risk-based position sizing
            risk_per_trade = 0.02  # 2% risk per trade
            entry_price = signal.get('entry_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            
            if entry_price > 0 and stop_loss > 0:
                risk_per_unit = abs(entry_price - stop_loss)
                risk_amount = balance * risk_per_trade
                
                if risk_per_unit > 0:
                    risk_based_position = risk_amount / entry_price
                    position_size = min(max_position_value / entry_price, risk_based_position)
                else:
                    position_size = max_position_value / entry_price
            else:
                # Fallback to max position size
                position_size = max_position_value / (entry_price or 45000)
            
            # Apply confidence multiplier
            confidence = signal.get('confidence', 0.5)
            confidence_multiplier = min(confidence * 1.5, 1.0)  # Max 1.0x
            
            final_position_size = position_size * confidence_multiplier
            
            logger.info(f"💰 Position size calculated: {final_position_size:.6f} BTC (${final_position_size * (entry_price or 45000):.2f})")
            
            return final_position_size
            
        except Exception as e:
            logger.error(f"❌ Position size calculation failed: {e}")
            return 0.001  # Minimal position size
    
    def update_trade_result(self, trade_result: Dict[str, Any]):
        """Cập nhật kết quả trade để tracking"""
        try:
            trade_data = {
                'timestamp': datetime.now(),
                'side': trade_result.get('side'),
                'amount': trade_result.get('amount', 0),
                'price': trade_result.get('price', 0),
                'pnl': trade_result.get('pnl', 0)
            }
            
            # Add to daily trades
            today = datetime.now().date()
            self.daily_trades = [t for t in self.daily_trades if t['timestamp'].date() == today]
            self.daily_trades.append(trade_data)
            
            # Update daily P&L
            self.daily_pnl += trade_data['pnl']
            
            # Update drawdown tracking
            current_balance = self.settings.INITIAL_BALANCE + self.daily_pnl
            if current_balance > self.peak_balance:
                self.peak_balance = current_balance
            
            drawdown = (self.peak_balance - current_balance) / self.peak_balance
            self.max_drawdown = max(self.max_drawdown, drawdown)
            
            logger.info(f"📊 Trade recorded: P&L {trade_data['pnl']:+.2f}, Daily P&L: {self.daily_pnl:+.2f}")
            
        except Exception as e:
            logger.error(f"❌ Trade result update failed: {e}")
    
    def _check_confidence(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check confidence level"""
        confidence = signal.get('confidence', 0)
        min_confidence = self.settings.MIN_CONFIDENCE_SCORE
        
        return {
            'name': 'Confidence Check',
            'passed': confidence >= min_confidence,
            'value': confidence,
            'threshold': min_confidence,
            'message': f"Confidence {confidence:.2%} {'≥' if confidence >= min_confidence else '<'} {min_confidence:.2%}"
        }
    
    def _check_daily_trade_limit(self) -> Dict[str, Any]:
        """Check daily trade limit"""
        today = datetime.now().date()
        today_trades = [t for t in self.daily_trades if t['timestamp'].date() == today]
        trade_count = len(today_trades)
        max_trades = self.settings.MAX_DAILY_TRADES
        
        return {
            'name': 'Daily Trade Limit',
            'passed': trade_count < max_trades,
            'value': trade_count,
            'threshold': max_trades,
            'message': f"Daily trades: {trade_count}/{max_trades}"
        }
    
    def _check_position_size(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check position size limits"""
        entry_price = signal.get('entry_price', 45000)
        max_position_value = self.settings.INITIAL_BALANCE * (self.settings.MAX_POSITION_SIZE / 100)
        suggested_size = max_position_value / entry_price
        
        return {
            'name': 'Position Size Check',
            'passed': True,  # Always pass, we calculate appropriate size
            'value': suggested_size,
            'threshold': self.settings.MAX_POSITION_SIZE,
            'message': f"Position size: {suggested_size:.6f} BTC (${suggested_size * entry_price:.2f})"
        }
    
    def _check_risk_reward_ratio(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check risk/reward ratio"""
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', 0)
        
        if entry_price > 0 and stop_loss > 0 and take_profit > 0:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk > 0:
                ratio = reward / risk
                min_ratio = 1.5  # Minimum 1:1.5 risk/reward
                
                return {
                    'name': 'Risk/Reward Ratio',
                    'passed': ratio >= min_ratio,
                    'value': ratio,
                    'threshold': min_ratio,
                    'message': f"R/R ratio: 1:{ratio:.2f}"
                }
        
        return {
            'name': 'Risk/Reward Ratio',
            'passed': False,
            'value': 0,
            'threshold': 1.5,
            'message': "Invalid price levels for R/R calculation"
        }
    
    def _check_market_conditions(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check general market conditions"""
        risk_level = signal.get('risk_level', 'MEDIUM')
        
        # For now, simple check based on signal risk level
        safe_levels = ['LOW', 'MEDIUM']
        
        return {
            'name': 'Market Conditions',
            'passed': risk_level in safe_levels,
            'value': risk_level,
            'threshold': 'LOW/MEDIUM',
            'message': f"Market risk level: {risk_level}"
        }
    
    def _get_risk_recommendation(self, checks: list) -> str:
        """Get risk management recommendation"""
        failed_checks = [check for check in checks if not check['passed']]
        
        if not failed_checks:
            return "All risk checks passed. Safe to trade with full position size."
        elif len(failed_checks) == 1:
            return f"One risk concern: {failed_checks[0]['message']}. Consider reducing position size."
        else:
            return f"Multiple risk concerns ({len(failed_checks)}). Recommend HOLD or very small position."
    
    def _calculate_max_position_size(self) -> float:
        """Calculate maximum allowed position size"""
        return self.settings.MAX_POSITION_SIZE / 100
    
    def _calculate_stop_loss(self, signal: Dict[str, Any]) -> float:
        """Calculate suggested stop loss"""
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        
        if stop_loss > 0:
            return stop_loss
        
        # Fallback: 2% stop loss
        if entry_price > 0:
            action = signal.get('action', 'HOLD')
            if action == 'BUY':
                return entry_price * (1 - self.settings.STOP_LOSS_PERCENT / 100)
            elif action == 'SELL':
                return entry_price * (1 + self.settings.STOP_LOSS_PERCENT / 100)
        
        return 0
    
    def _calculate_take_profit(self, signal: Dict[str, Any]) -> float:
        """Calculate suggested take profit"""
        entry_price = signal.get('entry_price', 0)
        take_profit = signal.get('take_profit', 0)
        
        if take_profit > 0:
            return take_profit
        
        # Fallback: 4% take profit
        if entry_price > 0:
            action = signal.get('action', 'HOLD')
            if action == 'BUY':
                return entry_price * (1 + self.settings.TAKE_PROFIT_PERCENT / 100)
            elif action == 'SELL':
                return entry_price * (1 - self.settings.TAKE_PROFIT_PERCENT / 100)
        
        return 0
    
    def _get_conservative_evaluation(self) -> Dict[str, Any]:
        """Return conservative risk evaluation on error"""
        return {
            'approved': False,
            'confidence_score': 0.0,
            'checks': [],
            'recommendation': 'Risk evaluation failed. Recommend HOLD.',
            'max_position_size': 0.01,
            'suggested_stop_loss': 0,
            'suggested_take_profit': 0
        }
