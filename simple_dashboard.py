"""
Simple Dashboard với dữ liệu mẫu real-time
"""
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import asyncio
import threading
import time
import random
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bitcoin-ai-bot-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data
bot_state = {
    'running': False,
    'demo_mode': True,
    'ai_connected': True,
    'current_price': 67500,
    'signal': {
        'action': 'BUY',
        'confidence': 0.75,
        'reasoning': 'AI analysis cho thấy xu hướng tăng với RSI oversold và volume cao'
    }
}

SIMPLE_DASHBOARD = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bitcoin AI Trading Bot - Simple Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { 
            font-family: Arial; 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px); 
        }
        .card h3 { 
            color: #ffd700; 
            border-bottom: 2px solid #ffd700; 
            padding-bottom: 10px; 
        }
        .price { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #00ff88; 
            text-align: center; 
            margin: 20px 0; 
        }
        .signal { 
            font-size: 1.5rem; 
            text-align: center; 
            padding: 15px; 
            border-radius: 10px; 
            margin: 10px 0; 
        }
        .signal.buy { background: rgba(0,255,136,0.2); color: #00ff88; }
        .signal.sell { background: rgba(255,68,68,0.2); color: #ff4444; }
        .signal.hold { background: rgba(255,170,0,0.2); color: #ffaa00; }
        .btn { 
            padding: 10px 20px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            margin: 5px; 
            font-weight: bold; 
        }
        .btn-success { background: #4CAF50; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .btn-info { background: #2196F3; color: white; }
        .status { 
            display: inline-block; 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.9rem; 
        }
        .status.online { background: #4CAF50; }
        .status.offline { background: #f44336; }
        .status.demo { background: #ff9800; }
        .log { 
            background: rgba(0,0,0,0.3); 
            padding: 15px; 
            border-radius: 10px; 
            height: 200px; 
            overflow-y: auto; 
            font-family: monospace; 
            font-size: 0.9rem; 
        }
        .log-entry { 
            margin-bottom: 5px; 
            padding-left: 10px; 
            border-left: 3px solid #ffd700; 
        }
        .indicator { 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            display: inline-block; 
            margin-right: 8px; 
        }
        .indicator.green { background: #00ff88; }
        .indicator.red { background: #ff4444; }
    </style>
</head>
<body>
    <h1>🤖 Bitcoin AI Trading Bot Dashboard</h1>
    
    <div class="container">
        <!-- Status Card -->
        <div class="card">
            <h3>📊 Bot Status</h3>
            <p><span class="indicator" id="ai-indicator"></span>AI: <span id="ai-status">Checking...</span></p>
            <p>Bot: <span class="status" id="bot-status">STOPPED</span></p>
            <p>Mode: <span class="status demo" id="mode-status">DEMO</span></p>
            <br>
            <button class="btn btn-success" onclick="startBot()">Start Bot</button>
            <button class="btn btn-danger" onclick="stopBot()">Stop Bot</button>
            <button class="btn btn-info" onclick="testAI()">Test AI</button>
        </div>

        <!-- Price Card -->
        <div class="card">
            <h3>💰 Bitcoin Price</h3>
            <div class="price" id="price">$67,500</div>
            <p>24h Change: <span id="change">+2.5%</span></p>
            <p>Volume: <span id="volume">1.8M</span></p>
            <p>Last Update: <span id="last-update">--:--:--</span></p>
        </div>

        <!-- Signal Card -->
        <div class="card">
            <h3>🎯 AI Trading Signal</h3>
            <div class="signal buy" id="signal">BUY</div>
            <p>Confidence: <span id="confidence">75%</span></p>
            <p>Entry: $<span id="entry">67,000</span></p>
            <p>Stop Loss: $<span id="stop-loss">65,500</span></p>
            <p>Take Profit: $<span id="take-profit">68,500</span></p>
            <p id="reasoning">AI analysis cho thấy xu hướng tăng với RSI oversold và volume cao</p>
        </div>

        <!-- Performance Card -->
        <div class="card">
            <h3>📈 Performance</h3>
            <p>Total Trades: <span id="total-trades">0</span></p>
            <p>Win Rate: <span id="win-rate">0%</span></p>
            <p>Profit/Loss: $<span id="profit-loss">0</span></p>
            <p>Balance: $<span id="balance">10,000</span></p>
        </div>

        <!-- Technical Indicators -->
        <div class="card">
            <h3>📊 Technical Analysis</h3>
            <p>RSI: <span id="rsi">42</span></p>
            <p>MACD: <span id="macd">150</span></p>
            <p>Support: $<span id="support">66,000</span></p>
            <p>Resistance: $<span id="resistance">68,000</span></p>
        </div>

        <!-- Activity Log -->
        <div class="card" style="grid-column: 1 / -1;">
            <h3>📝 Activity Log</h3>
            <div class="log" id="log">
                <div class="log-entry">[18:30:00] Dashboard started</div>
                <div class="log-entry">[18:30:01] AI connection established</div>
                <div class="log-entry">[18:30:02] Demo mode activated</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        
        // Connect event
        socket.on('connect', function() {
            addLog('WebSocket connected successfully');
            updateStatus();
        });

        // Real-time updates
        socket.on('price_update', function(data) {
            document.getElementById('price').textContent = `$${data.price.toLocaleString()}`;
            document.getElementById('change').textContent = `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)}%`;
            document.getElementById('volume').textContent = `${(data.volume / 1000000).toFixed(1)}M`;
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            addLog(`Price updated: $${data.price.toLocaleString()}`);
        });

        socket.on('signal_update', function(data) {
            const signalEl = document.getElementById('signal');
            signalEl.textContent = data.action;
            signalEl.className = `signal ${data.action.toLowerCase()}`;
            
            document.getElementById('confidence').textContent = `${Math.round(data.confidence * 100)}%`;
            document.getElementById('entry').textContent = data.entry_price.toLocaleString();
            document.getElementById('stop-loss').textContent = data.stop_loss.toLocaleString();
            document.getElementById('take-profit').textContent = data.take_profit.toLocaleString();
            document.getElementById('reasoning').textContent = data.reasoning || 'No reasoning provided';
            
            addLog(`New signal: ${data.action} (${Math.round(data.confidence * 100)}% confidence)`);
        });

        socket.on('ai_status', function(data) {
            const indicator = document.getElementById('ai-indicator');
            const status = document.getElementById('ai-status');
            
            if (data.connected) {
                indicator.className = 'indicator green';
                status.textContent = 'Connected';
            } else {
                indicator.className = 'indicator red';
                status.textContent = 'Disconnected';
            }
        });

        socket.on('bot_status', function(data) {
            const botStatus = document.getElementById('bot-status');
            botStatus.textContent = data.running ? 'RUNNING' : 'STOPPED';
            botStatus.className = data.running ? 'status online' : 'status offline';
            
            // Update performance data
            if (data.performance) {
                document.getElementById('total-trades').textContent = data.performance.total_trades || 0;
                document.getElementById('win-rate').textContent = `${data.performance.win_rate || 0}%`;
                document.getElementById('profit-loss').textContent = data.performance.profit_loss || 0;
                document.getElementById('balance').textContent = data.performance.balance || 10000;
            }
        });

        function addLog(message) {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `[${timestamp}] ${message}`;
            log.insertBefore(entry, log.firstChild);
            
            // Keep only last 50 entries
            while (log.children.length > 50) {
                log.removeChild(log.lastChild);
            }
        }

        function startBot() {
            socket.emit('start_bot');
            addLog('Starting bot...');
        }

        function stopBot() {
            socket.emit('stop_bot');
            addLog('Stopping bot...');
        }

        function testAI() {
            socket.emit('test_ai');
            addLog('Testing AI connection...');
        }

        function updateStatus() {
            // Send initial status update
            socket.emit('get_status');
        }

        // Initialize on page load
        window.onload = function() {
            addLog('Dashboard initialized');
            testAI(); // Test AI on load
            
            // Simulate some live data
            setTimeout(() => {
                socket.emit('get_live_data');
            }, 2000);
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(SIMPLE_DASHBOARD)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Send initial data
    emit('ai_status', {'connected': bot_state['ai_connected']})
    emit('bot_status', {'running': bot_state['running']})
    
    # Send current price
    emit('price_update', {
        'price': bot_state['current_price'],
        'change': random.uniform(-5, 5),
        'volume': random.randint(1000000, 3000000)
    })
    
    # Send current signal
    emit('signal_update', {
        'action': bot_state['signal']['action'],
        'confidence': bot_state['signal']['confidence'],
        'entry_price': bot_state['current_price'] - 500,
        'stop_loss': bot_state['current_price'] - 2000,
        'take_profit': bot_state['current_price'] + 1000,
        'reasoning': bot_state['signal']['reasoning']
    })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('start_bot')
def handle_start_bot():
    bot_state['running'] = True
    emit('bot_status', {'running': True})
    print("Bot started")

@socketio.on('stop_bot')
def handle_stop_bot():
    bot_state['running'] = False
    emit('bot_status', {'running': False})
    print("Bot stopped")

@socketio.on('test_ai')
def handle_test_ai():
    # Simulate AI test
    bot_state['ai_connected'] = True
    emit('ai_status', {'connected': True})
    print("AI test completed")

@socketio.on('get_status')
def handle_get_status():
    emit('ai_status', {'connected': bot_state['ai_connected']})
    emit('bot_status', {'running': bot_state['running']})

@socketio.on('get_live_data')
def handle_get_live_data():
    # Simulate getting live data
    new_price = bot_state['current_price'] + random.randint(-1000, 1000)
    bot_state['current_price'] = new_price
    
    emit('price_update', {
        'price': new_price,
        'change': random.uniform(-3, 3),
        'volume': random.randint(1200000, 2500000)
    })

def simulate_live_data():
    """Background thread to simulate live price updates"""
    while True:
        time.sleep(10)  # Update every 10 seconds
        
        # Random price movement
        change = random.randint(-500, 500)
        bot_state['current_price'] += change
        
        # Broadcast to all connected clients
        socketio.emit('price_update', {
            'price': bot_state['current_price'],
            'change': random.uniform(-2, 2),
            'volume': random.randint(1500000, 2200000)
        })
        
        # Occasionally send new AI signals
        if random.random() < 0.3:  # 30% chance
            actions = ['BUY', 'SELL', 'HOLD']
            new_action = random.choice(actions)
            bot_state['signal']['action'] = new_action
            
            socketio.emit('signal_update', {
                'action': new_action,
                'confidence': random.uniform(0.6, 0.9),
                'entry_price': bot_state['current_price'],
                'stop_loss': bot_state['current_price'] - random.randint(1000, 2000),
                'take_profit': bot_state['current_price'] + random.randint(1000, 2000),
                'reasoning': f'AI analysis updated với action {new_action}'
            })

if __name__ == '__main__':
    # Start background thread for live data
    import threading
    from flask import request
    
    bg_thread = threading.Thread(target=simulate_live_data, daemon=True)
    bg_thread.start()
    
    print("🚀 Starting Simple Bitcoin AI Dashboard...")
    print("📡 Dashboard running at: http://127.0.0.1:5001")
    print("🎯 Features: Live price, AI signals, bot controls")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
