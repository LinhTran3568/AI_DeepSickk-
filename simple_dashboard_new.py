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
    'capital': 10000,  # Vốn ban đầu
    'position_size': 0,  # Kích thước vị thế
    'next_action_time': 0,  # Thời gian hành động tiếp theo
    'signal': {
        'action': 'BUY',
        'confidence': 0.75,
        'entry_price': 0,
        'stop_loss': 0,
        'take_profit': 0,
        'time_to_action': 0,
        'hold_duration': 0,
        'reasoning': 'AI analysis cho thấy xu hướng tăng với RSI oversold và volume cao'
    }
}

SIMPLE_DASHBOARD = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 AI Bitcoin Trading Bot - Professional Dashboard</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #e2e8f0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #4f46e5, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.8;
            color: #94a3b8;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #4f46e5, #06b6d4, #10b981);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }

        .card h3 {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .price-card .price {
            font-size: 3rem;
            font-weight: 700;
            color: #10b981;
            text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
            margin-bottom: 15px;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }

        .stat-label {
            font-weight: 500;
            color: #94a3b8;
        }

        .stat-value {
            font-weight: 600;
            color: #e2e8f0;
        }

        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #f59e0b; }

        .signal-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .signal-buy { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
        .signal-sell { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
        .signal-hold { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }

        .btn {
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 5px;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
        }

        .btn-success { background: linear-gradient(45deg, #10b981, #059669); }
        .btn-danger { background: linear-gradient(45deg, #ef4444, #dc2626); }
        .btn-info { background: linear-gradient(45deg, #06b6d4, #0891b2); }
        .btn-warning { background: linear-gradient(45deg, #f59e0b, #d97706); }

        .input-group {
            margin-bottom: 15px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #94a3b8;
        }

        .input-group input, .input-group select {
            width: 100%;
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            color: #e2e8f0;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .input-group input:focus, .input-group select:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .prediction-section {
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(16, 185, 129, 0.1));
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
        }

        .countdown {
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin: 15px 0;
            color: #4f46e5;
            text-shadow: 0 0 20px rgba(79, 70, 229, 0.3);
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(148, 163, 184, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4f46e5, #06b6d4);
            transition: width 0.3s ease;
        }

        .log-container {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 12px;
            padding: 15px;
        }

        .log-entry {
            margin-bottom: 8px;
            padding: 8px 12px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            border-left: 3px solid #4f46e5;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        .status-online { background: #10b981; }
        .status-offline { background: #ef4444; }
        .status-warning { background: #f59e0b; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .capital-plan {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }

        .plan-item {
            background: rgba(15, 23, 42, 0.3);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }

        .plan-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #10b981;
        }

        .plan-label {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> AI Bitcoin Trading Bot</h1>
            <p>Dự đoán chính xác xu hướng Bitcoin với AI • Giao dịch thông minh • Quản lý vốn tối ưu</p>
        </div>

        <div class="dashboard-grid">
            <!-- Price Card -->
            <div class="card price-card">
                <h3><i class="fab fa-bitcoin"></i> Giá Bitcoin Real-time</h3>
                <div class="price" id="btcPrice">$116,727.62</div>
                <div class="stat-row">
                    <span class="stat-label">Thay đổi 24h:</span>
                    <span class="stat-value positive" id="priceChange">+0.32%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Volume 24h:</span>
                    <span class="stat-value" id="volume24h">$45.2B</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Market Cap:</span>
                    <span class="stat-value" id="marketCap">$2.31T</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Cập nhật:</span>
                    <span class="stat-value" id="lastUpdate">Đang tải...</span>
                </div>
            </div>

            <!-- AI Prediction Card -->
            <div class="card">
                <h3><i class="fas fa-brain"></i> Dự đoán AI Puter</h3>
                <div class="stat-row">
                    <span class="stat-label">Tín hiệu hiện tại:</span>
                    <span class="signal-badge signal-buy" id="aiSignal">BUY</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Độ tin cậy:</span>
                    <span class="stat-value positive" id="aiConfidence">90%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Giá mục tiêu:</span>
                    <span class="stat-value" id="targetPrice">$118,500</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Phân tích:</span>
                    <span class="stat-value" id="aiAnalysis">Xu hướng tăng mạnh</span>
                </div>
                
                <div class="prediction-section">
                    <h4><i class="fas fa-clock"></i> Thời gian dự đoán</h4>
                    <div class="countdown" id="predictionCountdown">--:--</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                    <p style="text-align: center; font-size: 0.9rem; opacity: 0.8;">
                        <span id="nextAction">Dự đoán sẽ mua trong</span> <span id="timeRemaining">--</span> giây
                    </p>
                </div>
            </div>

            <!-- Capital Management Card -->
            <div class="card">
                <h3><i class="fas fa-wallet"></i> Quản lý vốn</h3>
                <div class="input-group">
                    <label for="capitalInput">Vốn giao dịch (USD):</label>
                    <input type="number" id="capitalInput" value="10000" min="100" max="1000000" step="100">
                </div>
                <div class="input-group">
                    <label for="riskPercent">Rủi ro mỗi lệnh (%):</label>
                    <input type="number" id="riskPercent" value="2" min="0.5" max="10" step="0.5">
                </div>
                <div class="capital-plan">
                    <div class="plan-item">
                        <div class="plan-value" id="positionSize">$200</div>
                        <div class="plan-label">Khối lượng lệnh</div>
                    </div>
                    <div class="plan-item">
                        <div class="plan-value" id="maxRisk">$200</div>
                        <div class="plan-label">Rủi ro tối đa</div>
                    </div>
                    <div class="plan-item">
                        <div class="plan-value" id="stopLoss">$115,500</div>
                        <div class="plan-label">Stop Loss</div>
                    </div>
                    <div class="plan-item">
                        <div class="plan-value" id="takeProfit">$119,000</div>
                        <div class="plan-label">Take Profit</div>
                    </div>
                </div>
                <button class="btn btn-info" onclick="calculatePlan()">
                    <i class="fas fa-calculator"></i> Tính toán kế hoạch
                </button>
            </div>

            <!-- Trading Status Card -->
            <div class="card">
                <h3><i class="fas fa-chart-line"></i> Trạng thái giao dịch</h3>
                <div class="stat-row">
                    <span class="stat-label">Trạng thái Bot:</span>
                    <span class="stat-value">
                        <span class="status-indicator status-online"></span>
                        <span id="botStatus">Online</span>
                    </span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Vị thế hiện tại:</span>
                    <span class="stat-value neutral" id="currentPosition">Không có</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">P&L hôm nay:</span>
                    <span class="stat-value positive" id="dailyPnL">+$125.50</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Thời gian giữ lệnh:</span>
                    <span class="stat-value" id="holdDuration">--</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Kế hoạch bán:</span>
                    <span class="stat-value" id="sellPlan">Chờ tín hiệu</span>
                </div>
            </div>

            <!-- Control Panel Card -->
            <div class="card">
                <h3><i class="fas fa-cogs"></i> Điều khiển Bot</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <button class="btn btn-success" onclick="startBot()">
                        <i class="fas fa-play"></i> Khởi động Bot
                    </button>
                    <button class="btn btn-danger" onclick="stopBot()">
                        <i class="fas fa-stop"></i> Dừng Bot
                    </button>
                    <button class="btn btn-info" onclick="refreshData()">
                        <i class="fas fa-sync"></i> Refresh Data
                    </button>
                    <button class="btn btn-warning" onclick="resetBot()">
                        <i class="fas fa-redo"></i> Reset Bot
                    </button>
                </div>
                
                <div class="input-group" style="margin-top: 15px;">
                    <label for="tradingMode">Chế độ giao dịch:</label>
                    <select id="tradingMode">
                        <option value="demo">Demo (An toàn)</option>
                        <option value="live">Live (Thật)</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label for="autoTrade">Tự động giao dịch:</label>
                    <select id="autoTrade">
                        <option value="false">Tắt - Chỉ cảnh báo</option>
                        <option value="true">Bật - Giao dịch tự động</option>
                    </select>
                </div>
            </div>

            <!-- Technical Analysis Card -->
            <div class="card">
                <h3><i class="fas fa-chart-bar"></i> Phân tích kỹ thuật</h3>
                <div class="stat-row">
                    <span class="stat-label">RSI (14):</span>
                    <span class="stat-value neutral" id="rsiValue">65.2</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">MACD:</span>
                    <span class="stat-value positive" id="macdValue">Tăng</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">EMA 20/50:</span>
                    <span class="stat-value positive" id="emaValue">Bullish</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Volume:</span>
                    <span class="stat-value positive" id="volumeAnalysis">Cao</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Support:</span>
                    <span class="stat-value" id="supportLevel">$115,200</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Resistance:</span>
                    <span class="stat-value" id="resistanceLevel">$118,800</span>
                </div>
            </div>
        </div>

        <!-- Activity Log -->
        <div class="card">
            <h3><i class="fas fa-history"></i> Nhật ký hoạt động</h3>
            <div class="log-container" id="activityLog">
                <div class="log-entry">
                    <strong>[{{ timestamp }}]</strong> 🚀 Bot đã khởi động thành công
                </div>
                <div class="log-entry">
                    <strong>[{{ timestamp }}]</strong> 📊 Đang thu thập dữ liệu thị trường...
                </div>
                <div class="log-entry">
                    <strong>[{{ timestamp }}]</strong> 🤖 AI Puter phân tích: Tín hiệu BUY với 90% tin cậy
                </div>
                <div class="log-entry">
                    <strong>[{{ timestamp }}]</strong> 💰 Dự đoán: Mua trong 45 giây nữa
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let predictionTimer = null;
        let countdownSeconds = 0;

        // Real-time data updates
        socket.on('market_update', function(data) {
            updateMarketData(data);
        });

        socket.on('ai_prediction', function(data) {
            updateAIPrediction(data);
        });

        socket.on('bot_status', function(data) {
            updateBotStatus(data);
        });

        function updateMarketData(data) {
            document.getElementById('btcPrice').textContent = `$${data.price?.toLocaleString() || '116,727.62'}`;
            document.getElementById('priceChange').textContent = data.change || '+0.32%';
            document.getElementById('priceChange').className = `stat-value ${data.change?.startsWith('+') ? 'positive' : 'negative'}`;
            document.getElementById('volume24h').textContent = data.volume || '$45.2B';
            document.getElementById('marketCap').textContent = data.market_cap || '$2.31T';
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('vi-VN');

            // Update technical indicators
            document.getElementById('rsiValue').textContent = data.rsi || '65.2';
            document.getElementById('macdValue').textContent = data.macd || 'Tăng';
            document.getElementById('emaValue').textContent = data.ema || 'Bullish';
            document.getElementById('volumeAnalysis').textContent = data.volume_analysis || 'Cao';
            document.getElementById('supportLevel').textContent = data.support || '$115,200';
            document.getElementById('resistanceLevel').textContent = data.resistance || '$118,800';
        }

        function updateAIPrediction(data) {
            const signal = data.signal || 'BUY';
            const confidence = data.confidence || '90%';
            
            document.getElementById('aiSignal').textContent = signal;
            document.getElementById('aiSignal').className = `signal-badge signal-${signal.toLowerCase()}`;
            document.getElementById('aiConfidence').textContent = confidence;
            document.getElementById('targetPrice').textContent = data.target_price || '$118,500';
            document.getElementById('aiAnalysis').textContent = data.analysis || 'Xu hướng tăng mạnh';

            // Start prediction countdown
            if (data.next_signal_seconds) {
                startPredictionCountdown(data.next_signal_seconds, signal);
            }
        }

        function updateBotStatus(data) {
            document.getElementById('botStatus').textContent = data.status || 'Online';
            document.getElementById('currentPosition').textContent = data.position || 'Không có';
            document.getElementById('dailyPnL').textContent = data.pnl || '+$125.50';
            document.getElementById('holdDuration').textContent = data.hold_duration || '--';
            document.getElementById('sellPlan').textContent = data.sell_plan || 'Chờ tín hiệu';
        }

        function startPredictionCountdown(seconds, action) {
            countdownSeconds = seconds;
            const actionText = action === 'BUY' ? 'mua' : (action === 'SELL' ? 'bán' : 'đánh giá');
            
            document.getElementById('nextAction').textContent = `Dự đoán sẽ ${actionText} trong`;
            
            if (predictionTimer) clearInterval(predictionTimer);
            
            predictionTimer = setInterval(() => {
                if (countdownSeconds > 0) {
                    const minutes = Math.floor(countdownSeconds / 60);
                    const secs = countdownSeconds % 60;
                    document.getElementById('predictionCountdown').textContent = 
                        `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                    document.getElementById('timeRemaining').textContent = countdownSeconds;
                    
                    // Update progress bar
                    const progress = ((seconds - countdownSeconds) / seconds) * 100;
                    document.getElementById('progressFill').style.width = `${progress}%`;
                    
                    countdownSeconds--;
                } else {
                    document.getElementById('predictionCountdown').textContent = '00:00';
                    document.getElementById('timeRemaining').textContent = '0';
                    document.getElementById('progressFill').style.width = '100%';
                    clearInterval(predictionTimer);
                    
                    // Add to activity log
                    addLogEntry(`🎯 Thời điểm ${actionText} dự đoán đã đến!`);
                }
            }, 1000);
        }

        function calculatePlan() {
            const capital = parseFloat(document.getElementById('capitalInput').value) || 10000;
            const riskPercent = parseFloat(document.getElementById('riskPercent').value) || 2;
            const currentPrice = parseFloat(document.getElementById('btcPrice').textContent.replace(/[$,]/g, '')) || 116727;
            
            const riskAmount = capital * (riskPercent / 100);
            const positionSize = Math.min(riskAmount * 5, capital * 0.1); // Max 10% of capital
            const stopLossPrice = currentPrice * 0.98; // 2% stop loss
            const takeProfitPrice = currentPrice * 1.04; // 4% take profit
            
            document.getElementById('positionSize').textContent = `$${positionSize.toFixed(0)}`;
            document.getElementById('maxRisk').textContent = `$${riskAmount.toFixed(0)}`;
            document.getElementById('stopLoss').textContent = `$${stopLossPrice.toLocaleString()}`;
            document.getElementById('takeProfit').textContent = `$${takeProfitPrice.toLocaleString()}`;
            
            addLogEntry(`💡 Kế hoạch vốn đã được tính: Position $${positionSize.toFixed(0)}, Risk $${riskAmount.toFixed(0)}`);
        }

        function addLogEntry(message) {
            const logContainer = document.getElementById('activityLog');
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `<strong>[${new Date().toLocaleTimeString('vi-VN')}]</strong> ${message}`;
            logContainer.insertBefore(logEntry, logContainer.firstChild);
            
            // Keep only last 20 entries
            while (logContainer.children.length > 20) {
                logContainer.removeChild(logContainer.lastChild);
            }
        }

        function startBot() {
            fetch('/start_bot', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    addLogEntry('🚀 ' + data.message);
                });
        }

        function stopBot() {
            fetch('/stop_bot', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    addLogEntry('⏹️ ' + data.message);
                });
        }

        function refreshData() {
            fetch('/refresh_data', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    addLogEntry('🔄 Dữ liệu đã được cập nhật');
                    location.reload();
                });
        }

        function resetBot() {
            if (confirm('Bạn có chắc muốn reset bot? Tất cả dữ liệu sẽ được làm mới.')) {
                fetch('/reset_bot', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        addLogEntry('🔄 ' + data.message);
                        location.reload();
                    });
            }
        }

        // Auto-refresh data every 30 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateMarketData(data.market || {});
                    updateAIPrediction(data.ai || {});
                    updateBotStatus(data.bot || {});
                })
                .catch(error => {
                    console.log('Auto-refresh failed:', error);
                });
        }, 30000);

        // Initialize capital calculation on page load
        document.addEventListener('DOMContentLoaded', function() {
            calculatePlan();
            
            // Add event listeners for real-time calculation
            document.getElementById('capitalInput').addEventListener('input', calculatePlan);
            document.getElementById('riskPercent').addEventListener('input', calculatePlan);
            
            // Start with a demo prediction countdown
            startPredictionCountdown(45, 'BUY');
        });
    </script>
</body>
</html>
'''


def get_sample_market_data():
    """Tạo dữ liệu thị trường mẫu"""
    base_price = bot_state['current_price']
    change_percent = random.uniform(-2, 2)
    new_price = base_price * (1 + change_percent/100)
    bot_state['current_price'] = new_price
    
    return {
        'price': new_price,
        'change': f"{'+' if change_percent > 0 else ''}{change_percent:.2f}%",
        'volume': f"${random.uniform(40, 60):.1f}B",
        'market_cap': f"${random.uniform(2.2, 2.4):.2f}T",
        'rsi': round(random.uniform(30, 80), 1),
        'macd': random.choice(['Tăng', 'Giảm', 'Trung tính']),
        'ema': random.choice(['Bullish', 'Bearish', 'Sideways']),
        'volume_analysis': random.choice(['Cao', 'Trung bình', 'Thấp']),
        'support': f"${new_price * 0.97:.0f}",
        'resistance': f"${new_price * 1.03:.0f}"
    }

def get_sample_ai_prediction():
    """Tạo dự đoán AI mẫu"""
    signals = ['BUY', 'SELL', 'HOLD']
    signal = random.choice(signals)
    confidence = random.randint(75, 95)
    
    current_price = bot_state['current_price']
    if signal == 'BUY':
        target_price = current_price * random.uniform(1.02, 1.05)
        analysis = random.choice([
            'Xu hướng tăng mạnh với khối lượng cao',
            'RSI oversold, MACD tích cực',
            'Vượt qua vùng kháng cự quan trọng'
        ])
    elif signal == 'SELL':
        target_price = current_price * random.uniform(0.95, 0.98)
        analysis = random.choice([
            'Tín hiệu bán mạnh, áp lực giảm giá',
            'RSI overbought, MACD tiêu cực',
            'Không vượt được vùng kháng cự'
        ])
    else:
        target_price = current_price * random.uniform(0.99, 1.01)
        analysis = random.choice([
            'Thị trường sideway, chờ tín hiệu rõ ràng',
            'Khối lượng thấp, thiếu momentum',
            'Dao động trong vùng hỗ trợ - kháng cự'
        ])
    
    return {
        'signal': signal,
        'confidence': f"{confidence}%",
        'target_price': f"${target_price:.0f}",
        'analysis': analysis,
        'next_signal_seconds': random.randint(30, 120)
    }

def get_sample_bot_status():
    """Tạo trạng thái bot mẫu"""
    positions = ['Không có', 'Long BTC/USDT', 'Short BTC/USDT']
    pnl_values = ['+$125.50', '-$45.30', '+$89.20', '+$156.75', '-$23.10']
    
    return {
        'status': 'Online' if bot_state['running'] else 'Offline',
        'position': random.choice(positions),
        'pnl': random.choice(pnl_values),
        'hold_duration': f"{random.randint(5, 120)} phút" if random.choice([True, False]) else '--',
        'sell_plan': random.choice(['Chờ tín hiệu', 'Take profit tại $118,500', 'Stop loss tại $115,200'])
    }

@app.route('/')
def dashboard():
    timestamp = datetime.now().strftime('%H:%M:%S')
    return render_template_string(SIMPLE_DASHBOARD, timestamp=timestamp)

@app.route('/api/status')
def api_status():
    """API endpoint để lấy dữ liệu real-time"""
    return {
        'market': get_sample_market_data(),
        'ai': get_sample_ai_prediction(),
        'bot': get_sample_bot_status(),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/start_bot', methods=['POST'])
def start_bot():
    bot_state['running'] = True
    socketio.emit('bot_status', {'status': 'Bot đã khởi động'})
    return {'message': 'Bot đã được khởi động thành công!'}

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    bot_state['running'] = False
    socketio.emit('bot_status', {'status': 'Bot đã dừng'})
    return {'message': 'Bot đã được dừng!'}

@app.route('/refresh_data', methods=['POST'])
def refresh_data():
    # Emit new data to all connected clients
    socketio.emit('market_update', get_sample_market_data())
    socketio.emit('ai_prediction', get_sample_ai_prediction())
    socketio.emit('bot_status', get_sample_bot_status())
    return {'message': 'Dữ liệu đã được làm mới!'}

@app.route('/reset_bot', methods=['POST'])
def reset_bot():
    bot_state.update({
        'running': False,
        'demo_mode': True,
        'ai_connected': True,
        'current_price': 67500,
        'capital': 10000,
        'position_size': 0,
        'next_action_time': 0
    })
    return {'message': 'Bot đã được reset về trạng thái ban đầu!'}

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial data
    emit('market_update', get_sample_market_data())
    emit('ai_prediction', get_sample_ai_prediction())
    emit('bot_status', get_sample_bot_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def background_data_emitter():
    """Gửi dữ liệu mẫu mỗi 30 giây"""
    while True:
        time.sleep(30)
        if bot_state['running']:
            socketio.emit('market_update', get_sample_market_data())
            socketio.emit('ai_prediction', get_sample_ai_prediction())
            socketio.emit('bot_status', get_sample_bot_status())

def start_background_thread():
    """Khởi động thread nền"""
    thread = threading.Thread(target=background_data_emitter, daemon=True)
    thread.start()

if __name__ == '__main__':
    print("🚀 Starting Bitcoin AI Trading Dashboard...")
    print("📊 Dashboard: http://localhost:8080")
    print("💹 Real-time data simulation active")
    print("🤖 AI predictions with countdown timers")
    print("💰 Capital management tools available")
    
    start_background_thread()
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
