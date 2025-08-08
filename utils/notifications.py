"""
Hệ thống thông báo cho Bitcoin Trading Bot
"""
import logging
from datetime import datetime
from typing import Dict, Any
from config.settings import Settings

logger = logging.getLogger(__name__)

class NotificationManager:
    """Quản lý thông báo và alerts"""
    
    def __init__(self):
        self.settings = Settings()
        self.enabled = self.settings.ENABLE_NOTIFICATIONS
        self.notification_type = self.settings.NOTIFICATION_TYPE
        
    def send_info(self, message: str):
        """Gửi thông báo thông tin"""
        if not self.enabled:
            return
            
        formatted_msg = f"ℹ️ INFO: {message}"
        self._send_notification(formatted_msg, "info")
    
    def send_warning(self, message: str):
        """Gửi cảnh báo"""
        if not self.enabled:
            return
            
        formatted_msg = f"⚠️ WARNING: {message}"
        self._send_notification(formatted_msg, "warning")
    
    def send_error(self, message: str):
        """Gửi thông báo lỗi"""
        if not self.enabled:
            return
            
        formatted_msg = f"❌ ERROR: {message}"
        self._send_notification(formatted_msg, "error")
    
    def send_trade_alert(self, trade_data: Dict[str, Any]):
        """Gửi alert về trade"""
        if not self.enabled:
            return
            
        action_emoji = "🟢" if trade_data.get('side') == 'buy' else "🔴"
        message = (
            f"{action_emoji} TRADE EXECUTED\n"
            f"Pair: {trade_data.get('symbol', 'N/A')}\n"
            f"Side: {trade_data.get('side', 'N/A').upper()}\n"
            f"Amount: {trade_data.get('amount', 'N/A')}\n"
            f"Price: ${trade_data.get('price', 'N/A')}\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        self._send_notification(message, "trade")
    
    def send_signal_alert(self, signal_data: Dict[str, Any]):
        """Gửi alert về signal"""
        if not self.enabled:
            return
            
        action_emoji = "🟢" if signal_data.get('action') == 'BUY' else "🔴"
        confidence = signal_data.get('confidence', 0)
        
        message = (
            f"{action_emoji} TRADING SIGNAL\n"
            f"Action: {signal_data.get('action', 'N/A')}\n"
            f"Confidence: {confidence:.2%}\n"
            f"Entry: ${signal_data.get('entry_price', 'N/A')}\n"
            f"Stop Loss: ${signal_data.get('stop_loss', 'N/A')}\n"
            f"Take Profit: ${signal_data.get('take_profit', 'N/A')}\n"
            f"Reason: {signal_data.get('reason', 'N/A')}"
        )
        
        self._send_notification(message, "signal")
    
    def send_portfolio_update(self, portfolio_data: Dict[str, Any]):
        """Gửi cập nhật portfolio"""
        if not self.enabled:
            return
            
        total_value = portfolio_data.get('total_value', 0)
        pnl = portfolio_data.get('pnl', 0)
        pnl_emoji = "📈" if pnl >= 0 else "📉"
        
        message = (
            f"💼 PORTFOLIO UPDATE\n"
            f"Total Value: ${total_value:,.2f}\n"
            f"{pnl_emoji} P&L: ${pnl:,.2f} ({portfolio_data.get('pnl_percent', 0):.2%})\n"
            f"Open Positions: {portfolio_data.get('open_positions', 0)}\n"
            f"Win Rate: {portfolio_data.get('win_rate', 0):.1%}"
        )
        
        self._send_notification(message, "portfolio")
    
    def send_system_alert(self, message: str, alert_type: str = "system"):
        """Gửi alert hệ thống"""
        if not self.enabled:
            return
            
        formatted_msg = f"🔧 SYSTEM: {message}"
        self._send_notification(formatted_msg, alert_type)
    
    def _send_notification(self, message: str, msg_type: str):
        """Gửi thông báo qua channel được cấu hình"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.notification_type == "console":
            self._send_console_notification(message, timestamp)
        elif self.notification_type == "email":
            self._send_email_notification(message, timestamp)
        elif self.notification_type == "telegram":
            self._send_telegram_notification(message, timestamp)
        else:
            logger.warning(f"Unknown notification type: {self.notification_type}")
    
    def _send_console_notification(self, message: str, timestamp: str):
        """Gửi thông báo ra console"""
        separator = "=" * 50
        print(f"\n{separator}")
        print(f"🤖 BITCOIN BOT NOTIFICATION - {timestamp}")
        print(separator)
        print(message)
        print(f"{separator}\n")
    
    def _send_email_notification(self, message: str, timestamp: str):
        """Gửi email notification (TODO: implement)"""
        # TODO: Implement email notifications
        logger.info(f"EMAIL notification: {message}")
    
    def _send_telegram_notification(self, message: str, timestamp: str):
        """Gửi Telegram notification (TODO: implement)"""
        # TODO: Implement Telegram notifications
        logger.info(f"TELEGRAM notification: {message}")
