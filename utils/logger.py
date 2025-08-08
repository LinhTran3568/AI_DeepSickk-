"""
Logging utilities cho Bitcoin Trading Bot
"""
import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter với màu sắc cho console"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format(self, record):
        # Add color to levelname
        levelname_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{levelname_color}{record.levelname}{Style.RESET_ALL}"
        
        # Format time
        record.asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        return super().format(record)

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logger với file và console handlers
    
    Args:
        name: Tên logger
        log_level: Mức log level
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # File handler with rotation
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        log_dir / "bitcoin_bot.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler with colors
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_trade(logger: logging.Logger, trade_data: dict):
    """
    Log chi tiết trade
    
    Args:
        logger: Logger instance
        trade_data: Dữ liệu trade
    """
    logger.info(f"🎯 TRADE EXECUTED: {trade_data}")

def log_signal(logger: logging.Logger, signal_data: dict):
    """
    Log signal trading
    
    Args:
        logger: Logger instance
        signal_data: Dữ liệu signal
    """
    action_emoji = "🟢" if signal_data.get('action') == 'BUY' else "🔴"
    logger.info(f"{action_emoji} SIGNAL: {signal_data}")

def log_performance(logger: logging.Logger, performance_data: dict):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        performance_data: Dữ liệu performance
    """
    logger.info(f"📊 PERFORMANCE: {performance_data}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict):
    """
    Log error với context
    
    Args:
        logger: Logger instance
        error: Exception
        context: Context data
    """
    logger.error(f"❌ ERROR: {error}")
    logger.debug(f"Context: {context}")

# Create main bot logger
bot_logger = setup_logger("BitcoinBot")
