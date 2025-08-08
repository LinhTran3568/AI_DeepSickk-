#!/usr/bin/env python3
"""
Bitcoin Trading Bot Dashboard
Web interface để theo dõi và điều khiển bot
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
from config.settings import Settings
from trading.exchange import ExchangeManager
from data.collector import DataCollector
from ai_engine.deepseek_client import DeepSeekClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bitcoin_bot_dashboard_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global components
settings = Settings()
exchange_manager = ExchangeManager()
data_collector = DataCollector()
deepseek_client = DeepSeekClient()

# Bot state
bot_state = {
    'running': False,
    'last_signal': None,
    'last_trade': None,
    'performance': {
        'total_pnl': 0,
        'total_trades': 0,
        'win_rate': 0,
        'best_trade': 0,
        'worst_trade': 0
    },
    'current_positions': [],
    'balance': {'USDT': 10000, 'BTC': 0}
}

@app.route('/')
def index():
    """Trang chủ dashboard"""
    return render_template('index.html', bot_state=bot_state)

@app.route('/api/status')
def get_status():
    """API endpoint cho bot status"""
    return jsonify({
        'status': 'running' if bot_state['running'] else 'stopped',
        'timestamp': datetime.now().isoformat(),
        'balance': bot_state['balance'],
        'positions': bot_state['current_positions'],
        'performance': bot_state['performance']
    })

@app.route('/api/market-data')
def get_market_data():
    """API endpoint cho market data"""
    try:
        # In a real implementation, this would be async
        # For demo, return mock data
        market_data = {
            'price': 45000,
            'change_24h': 2.5,
            'volume': 1500000000,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart-data')
def get_chart_data():
    """API endpoint cho chart data"""
    try:
        # Mock chart data - in real app, fetch from data collector
        timestamps = []
        prices = []
        base_price = 45000
        
        for i in range(100):
            timestamp = datetime.now() - timedelta(hours=100-i)
            price = base_price + (i * 10) + ((-1)**i * 200)  # Mock price movement
            timestamps.append(timestamp.isoformat())
            prices.append(price)
        
        chart_data = {
            'timestamps': timestamps,
            'prices': prices,
            'volumes': [1000000 + i * 1000 for i in range(100)]
        }
        
        return jsonify(chart_data)
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals')
def get_signals():
    """API endpoint cho trading signals"""
    try:
        signals = [
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'BUY',
                'confidence': 0.85,
                'price': 45000,
                'reason': 'AI prediction + RSI oversold'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'action': 'SELL',
                'confidence': 0.72,
                'price': 44800,
                'reason': 'Resistance level reached'
            }
        ]
        return jsonify(signals)
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """API endpoint cho trade history"""
    try:
        trades = [
            {
                'timestamp': datetime.now().isoformat(),
                'side': 'BUY',
                'amount': 0.001,
                'price': 45000,
                'pnl': 50,
                'status': 'completed'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'side': 'SELL',
                'amount': 0.001,
                'price': 44950,
                'pnl': -25,
                'status': 'completed'
            }
        ]
        return jsonify(trades)
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start trading bot"""
    try:
        bot_state['running'] = True
        logger.info("🚀 Bot started via dashboard")
        
        # Emit status update to all clients
        socketio.emit('bot_status_update', {
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop trading bot"""
    try:
        bot_state['running'] = False
        logger.info("🛑 Bot stopped via dashboard")
        
        # Emit status update to all clients
        socketio.emit('bot_status_update', {
            'status': 'stopped',
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def bot_settings():
    """Get/Update bot settings"""
    if request.method == 'GET':
        return jsonify({
            'max_position_size': settings.MAX_POSITION_SIZE,
            'stop_loss_percent': settings.STOP_LOSS_PERCENT,
            'take_profit_percent': settings.TAKE_PROFIT_PERCENT,
            'max_daily_trades': settings.MAX_DAILY_TRADES,
            'trading_pair': settings.TRADING_PAIR
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            # Update settings (in production, save to file/database)
            logger.info(f"Settings updated: {data}")
            return jsonify({'success': True, 'message': 'Settings updated'})
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('bot_status_update', {
        'status': 'running' if bot_state['running'] else 'stopped',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    emit('market_update', {
        'price': 45000,
        'change': 2.5,
        'timestamp': datetime.now().isoformat()
    })

def create_price_chart(chart_data):
    """Create price chart with Plotly"""
    try:
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=chart_data['timestamps'],
            y=chart_data['prices'],
            mode='lines',
            name='BTC Price',
            line=dict(color='#f7931a', width=2)
        ))
        
        # Customize layout
        fig.update_layout(
            title='Bitcoin Price Chart',
            xaxis_title='Time',
            yaxis_title='Price (USDT)',
            template='plotly_dark',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        return "{}"

# Background task to update dashboard
def background_updates():
    """Background task để cập nhật real-time data"""
    while True:
        try:
            if bot_state['running']:
                # Update market data
                socketio.emit('market_update', {
                    'price': 45000 + (datetime.now().second * 10),  # Mock price
                    'volume': 1500000000,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Update performance
                socketio.emit('performance_update', bot_state['performance'])
            
            socketio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Background update error: {e}")
            socketio.sleep(10)

# Template directory
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')
app.static_folder = os.path.join(os.path.dirname(__file__), 'static')

# Create templates directory if not exists
os.makedirs(app.template_folder, exist_ok=True)
os.makedirs(app.static_folder, exist_ok=True)

def main():
    """Main dashboard entry point"""
    try:
        logger.info("🖥️ Starting Bitcoin Trading Bot Dashboard...")
        
        # Start background updates
        socketio.start_background_task(background_updates)
        
        # Run dashboard
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=settings.FLASK_PORT, 
            debug=settings.FLASK_DEBUG
        )
        
    except Exception as e:
        logger.error(f"❌ Dashboard startup failed: {e}")

if __name__ == '__main__':
    main()
