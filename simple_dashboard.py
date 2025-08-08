"""
Simple Dashboard với AI Trading Engine thông minh và phân tích liên tục
"""
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import asyncio
import threading
import time
import random
import json
from datetime import datetime
from ai_trading_engine import ai_engine
from continuous_ai_analyzer import continuous_analyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bitcoin-ai-bot-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data với AI Engine
bot_state = {
    'running': False,
    'demo_mode': True,
    'ai_connected': True,
    'current_price': 116727.62,
    'capital': 10000,
    'position_size': 0,
    'next_action_time': 0,
    'current_timeframe': '15m',
    'active_trades': {},
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

        /* Trading Signals Panel Styles */
        .signal-status {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(79, 70, 229, 0.1));
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid rgba(16, 185, 129, 0.3);
        }

        .signal-main {
            text-align: center;
        }

        .signal-action {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }

        .action-text {
            font-size: 2rem;
            font-weight: 800;
            color: #10b981;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
            animation: pulse-glow 2s infinite;
        }

        .confidence-badge {
            background: linear-gradient(45deg, #10b981, #059669);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1.1rem;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }

        .signal-price {
            font-size: 1.2rem;
            color: #e2e8f0;
            font-weight: 600;
        }

        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }

        .btn-trade {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 15px;
            border: none;
            border-radius: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-trade i {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }

        .btn-trade span {
            font-size: 1rem;
            margin-bottom: 4px;
        }

        .btn-trade small {
            font-size: 0.8rem;
            opacity: 0.8;
        }

        .btn-buy {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        }

        .btn-buy:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(16, 185, 129, 0.4);
        }

        .btn-buy:active {
            transform: scale(0.95);
        }

        .btn-sell {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
        }

        .btn-sell:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(239, 68, 68, 0.4);
        }

        .btn-sell:active {
            transform: scale(0.95);
        }

        .btn-cancel {
            background: linear-gradient(135deg, #6b7280, #4b5563);
            color: white;
            box-shadow: 0 8px 25px rgba(107, 114, 128, 0.3);
        }

        .btn-cancel:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(107, 114, 128, 0.4);
        }

        .btn-cancel:active {
            transform: scale(0.95);
        }

        .trading-instructions {
            background: rgba(15, 23, 42, 0.3);
            border-radius: 12px;
            padding: 15px;
        }

        .instruction-item {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }

        .instruction-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }

        .instruction-icon {
            font-size: 1.2rem;
            min-width: 30px;
        }

        .instruction-text {
            font-weight: 500;
            color: #e2e8f0;
        }

        @keyframes pulse-glow {
            0%, 100% { 
                text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
                transform: scale(1);
            }
            50% { 
                text-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
                transform: scale(1.05);
            }
        }

        .signal-sell .action-text {
            color: #ef4444;
            text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
        }

        .signal-sell .confidence-badge {
            background: linear-gradient(45deg, #ef4444, #dc2626);
        }

        .signal-sell {
            border-color: rgba(239, 68, 68, 0.3);
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
        }

        .signal-hold .action-text {
            color: #f59e0b;
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
        }

        .signal-hold .confidence-badge {
            background: linear-gradient(45deg, #f59e0b, #d97706);
        }

        .signal-hold {
            border-color: rgba(245, 158, 11, 0.3);
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1));
        }

        .btn-disabled {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
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

            <!-- Trading Signals Panel - Rõ ràng và dễ sử dụng -->
            <div class="card">
                <h3><i class="fas fa-traffic-light"></i> Tín hiệu giao dịch</h3>
                
                <!-- Current Signal Status -->
                <div class="signal-status" id="signalStatus">
                    <div class="signal-main">
                        <div class="signal-action" id="currentAction">
                            <span class="action-text">MUA NGAY</span>
                            <span class="confidence-badge">92%</span>
                        </div>
                        <div class="signal-price" id="signalPrice">
                            Vào lệnh tại: $116,750
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="action-buttons">
                    <button class="btn-trade btn-buy" id="buyButton" onclick="executeBuy()">
                        <i class="fas fa-arrow-up"></i>
                        <span>MUA NGAY</span>
                        <small>$116,750</small>
                    </button>
                    <button class="btn-trade btn-sell" id="sellButton" onclick="executeSell()">
                        <i class="fas fa-arrow-down"></i>
                        <span>BÁN NGAY</span>
                        <small>$116,600</small>
                    </button>
                    <button class="btn-trade btn-cancel" id="cancelButton" onclick="cancelOrder()">
                        <i class="fas fa-times"></i>
                        <span>HỦY LỆNH</span>
                    </button>
                </div>
                
                <!-- Trading Instructions -->
                <div class="trading-instructions" id="tradingInstructions">
                    <div class="instruction-item">
                        <span class="instruction-icon">🎯</span>
                        <span class="instruction-text">Take Profit: $118,500</span>
                    </div>
                    <div class="instruction-item">
                        <span class="instruction-icon">🛡️</span>
                        <span class="instruction-text">Stop Loss: $115,200</span>
                    </div>
                    <div class="instruction-item">
                        <span class="instruction-icon">⏰</span>
                        <span class="instruction-text">Giữ lệnh: 15 phút</span>
                    </div>
                </div>
            </div>

            <!-- AI Continuous Analysis Card -->
            <div class="card">
                <h3><i class="fas fa-brain"></i> AI Phân tích liên tục</h3>
                <div class="stat-row">
                    <span class="stat-label">Trạng thái AI:</span>
                    <span class="stat-value">
                        <span class="status-indicator status-online"></span>
                        <span id="aiStatus">Đang phân tích...</span>
                    </span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Cập nhật cuối:</span>
                    <span class="stat-value" id="lastAnalysisUpdate">--:--:--</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Xu hướng:</span>
                    <span class="stat-value positive" id="trendDirection">Tăng mạnh</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Mức rủi ro:</span>
                    <span class="stat-value neutral" id="riskLevel">Trung bình</span>
                </div>
                
                <div class="prediction-section">
                    <h4><i class="fas fa-lightbulb"></i> Khuyến nghị AI</h4>
                    <div style="margin: 10px 0;">
                        <div id="aiRecommendations" style="font-size: 0.9rem; line-height: 1.4;">
                            <div>💹 Momentum tăng mạnh (+2.3%)</div>
                            <div>🔊 Volume rất cao (1.4x)</div>
                            <div>🟢 Áp lực mua mạnh (+5.2%)</div>
                        </div>
                    </div>
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
                <div class="stat-row">
                    <span class="stat-label">Khung thời gian:</span>
                    <span class="stat-value" id="currentTimeframe">15m</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Urgency:</span>
                    <span class="stat-value" id="signalUrgency">Medium</span>
                </div>
                
                <div class="input-group">
                    <label for="timeframeSelect">Khung thời gian:</label>
                    <select id="timeframeSelect" onchange="changeTimeframe()">
                        <option value="5m">5 phút (Scalping)</option>
                        <option value="15m" selected>15 phút (Day Trading)</option>
                        <option value="1h">1 giờ (Swing Trading)</option>
                        <option value="4h">4 giờ (Position Trading)</option>
                    </select>
                </div>
                
                <div class="prediction-section">
                    <h4><i class="fas fa-clock"></i> Kế hoạch giao dịch AI</h4>
                    <div class="countdown" id="predictionCountdown">--:--</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                    <p style="text-align: center; font-size: 0.9rem; opacity: 0.8;">
                        <span id="nextAction">Dự đoán sẽ mua trong</span> <span id="timeRemaining">--</span> phút
                    </p>
                    <div style="text-align: center; margin-top: 10px;">
                        <span style="font-size: 0.8rem; color: #94a3b8;">
                            Kế hoạch: <span id="tradePlan">Mua → Giữ 15 phút → Take profit</span>
                        </span>
                    </div>
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

            <!-- Real-time Strategy Plans -->
            <div class="card">
                <h3><i class="fas fa-strategy"></i> Kế hoạch trading real-time</h3>
                <div class="stat-row">
                    <span class="stat-label">5m Plan:</span>
                    <span class="stat-value" id="plan5m">Mua → 5 phút → TP $117,200</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">15m Plan:</span>
                    <span class="stat-value" id="plan15m">Mua → 15 phút → TP $118,500</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">1h Plan:</span>
                    <span class="stat-value" id="plan1h">Hold → 60 phút → Đánh giá</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">4h Plan:</span>
                    <span class="stat-value" id="plan4h">Bán → 240 phút → TP $115,800</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Khuyến nghị:</span>
                    <span class="stat-value positive" id="bestPlan">15m - Độ tin cậy cao</span>
                </div>
                <button class="btn btn-info" onclick="updatePlans()">
                    <i class="fas fa-sync"></i> Cập nhật kế hoạch
                </button>
            </div>

            <!-- Multi-Timeframe Analysis Card -->
            <div class="card">
                <h3><i class="fas fa-layer-group"></i> Phân tích đa khung thời gian</h3>
                <div class="stat-row">
                    <span class="stat-label">5m (Scalping):</span>
                    <span class="signal-badge signal-buy" id="signal5m">BUY</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">15m (Day Trading):</span>
                    <span class="signal-badge signal-buy" id="signal15m">BUY</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">1h (Swing Trading):</span>
                    <span class="signal-badge signal-hold" id="signal1h">HOLD</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">4h (Position):</span>
                    <span class="signal-badge signal-sell" id="signal4h">SELL</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Consensus:</span>
                    <span class="stat-value positive" id="consensus">Bullish (75%)</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Best Timeframe:</span>
                    <span class="stat-value" id="bestTimeframe">15m - High Probability</span>
                </div>
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

        socket.on('continuous_analysis', function(data) {
            updateContinuousAnalysis(data);
        });

        socket.on('strategy_plans', function(data) {
            updateStrategyPlans(data);
        });

        socket.on('bot_status', function(data) {
            updateBotStatus(data);
        });

        socket.on('trading_signal', function(data) {
            updateTradingSignals(data);
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
            document.getElementById('currentTimeframe').textContent = data.timeframe || '15m';
            document.getElementById('signalUrgency').textContent = data.urgency || 'Medium';
            document.getElementById('tradePlan').textContent = data.trade_plan || 'Mua → Giữ 15 phút → Take profit';

            // Start prediction countdown with minutes
            if (data.next_signal_minutes) {
                startPredictionCountdown(data.next_signal_minutes * 60, signal, data.next_signal_minutes);
            }
        }

        function updateContinuousAnalysis(data) {
            document.getElementById('aiStatus').textContent = 'Phân tích liên tục';
            document.getElementById('lastAnalysisUpdate').textContent = data.last_update || new Date().toLocaleTimeString('vi-VN');
            
            // Update trend direction with colors
            const trendElement = document.getElementById('trendDirection');
            const trendMap = {
                'strongly_up': {text: '📈 Tăng mạnh', class: 'positive'},
                'up': {text: '📊 Tăng', class: 'positive'},
                'strongly_down': {text: '📉 Giảm mạnh', class: 'negative'},
                'down': {text: '📊 Giảm', class: 'negative'},
                'sideways': {text: '➡️ Ngang', class: 'neutral'},
                'unknown': {text: '❓ Chưa rõ', class: 'neutral'}
            };
            
            const trend = trendMap[data.trend_direction] || trendMap.unknown;
            trendElement.textContent = trend.text;
            trendElement.className = `stat-value ${trend.class}`;
            
            // Update risk level
            const riskElement = document.getElementById('riskLevel');
            const riskMap = {
                'low': {text: '🟢 Thấp', class: 'positive'},
                'medium': {text: '🟡 Trung bình', class: 'neutral'},
                'high': {text: '🔴 Cao', class: 'negative'}
            };
            
            const risk = riskMap[data.risk_level] || riskMap.medium;
            riskElement.textContent = risk.text;
            riskElement.className = `stat-value ${risk.class}`;
            
            // Update AI recommendations
            const recommendationsContainer = document.getElementById('aiRecommendations');
            if (data.analysis_details && data.analysis_details.length > 0) {
                recommendationsContainer.innerHTML = data.analysis_details
                    .map(detail => `<div style="margin: 3px 0;">${detail}</div>`)
                    .join('');
            }
            
            addLogEntry(`🧠 AI: ${data.recommendation || 'Phân tích cập nhật'}`);
        }

        function updateStrategyPlans(data) {
            // Update individual timeframe plans
            if (data.plans_by_timeframe) {
                Object.keys(data.plans_by_timeframe).forEach(tf => {
                    const element = document.getElementById(`plan${tf}`);
                    if (element) {
                        element.textContent = data.plans_by_timeframe[tf];
                    }
                });
            }
            
            // Update best plan recommendation
            if (data.best_timeframe && data.best_plan) {
                document.getElementById('bestPlan').textContent = 
                    `${data.best_timeframe} - ${data.confidence} tin cậy`;
            }
            
            addLogEntry(`📋 Kế hoạch cập nhật: ${data.best_plan || 'Đang tính toán...'}`);
        }

        function updatePlans() {
            fetch('/update_plans', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    updateStrategyPlans(data);
                    addLogEntry('� Kế hoạch đã được cập nhật thủ công');
                });
        }

        function updateBotStatus(data) {
            document.getElementById('botStatus').textContent = data.status || 'Online';
            document.getElementById('currentPosition').textContent = data.position || 'Không có';
            document.getElementById('dailyPnL').textContent = data.pnl || '+$125.50';
            document.getElementById('holdDuration').textContent = data.hold_duration || '--';
            document.getElementById('sellPlan').textContent = data.sell_plan || 'Chờ tín hiệu';
        }

        function startPredictionCountdown(seconds, action, minutes) {
            countdownSeconds = seconds;
            const actionText = action === 'BUY' ? 'mua' : (action === 'SELL' ? 'bán' : 'đánh giá lại');
            
            document.getElementById('nextAction').textContent = `Dự đoán sẽ ${actionText} trong`;
            
            if (predictionTimer) clearInterval(predictionTimer);
            
            predictionTimer = setInterval(() => {
                if (countdownSeconds > 0) {
                    const mins = Math.floor(countdownSeconds / 60);
                    const secs = countdownSeconds % 60;
                    document.getElementById('predictionCountdown').textContent = 
                        `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
                    document.getElementById('timeRemaining').textContent = mins > 0 ? `${mins} phút ${secs} giây` : `${secs} giây`;
                    
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
                    addLogEntry(`🎯 Thời điểm ${actionText} dự đoán đã đến! Executing AI strategy...`);
                    
                    // Auto-refresh for next prediction
                    setTimeout(() => {
                        fetch('/api/status')
                            .then(response => response.json())
                            .then(data => {
                                updateAIPrediction(data.ai || {});
                            });
                    }, 2000);
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

        // Auto-refresh data every 10 seconds for continuous analysis
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateMarketData(data.market || {});
                    updateAIPrediction(data.ai || {});
                    updateBotStatus(data.bot || {});
                    
                    // Update continuous analysis
                    if (data.continuous_analysis) {
                        updateContinuousAnalysis(data.continuous_analysis);
                    }
                    
                    // Update strategy plans  
                    if (data.strategy_plans) {
                        updateStrategyPlans(data.strategy_plans);
                    }
                })
                .catch(error => {
                    console.log('Auto-refresh failed:', error);
                });
        }, 10000);  // Every 10 seconds for real-time feeling

        // Initialize capital calculation on page load
        document.addEventListener('DOMContentLoaded', function() {
            calculatePlan();
            
            // Add event listeners for real-time calculation
            document.getElementById('capitalInput').addEventListener('input', calculatePlan);
            document.getElementById('riskPercent').addEventListener('input', calculatePlan);
            
            // Start with AI prediction countdown - demo 15 minutes
            startPredictionCountdown(15 * 60, 'BUY', 15);
            
            // Set initial timeframe
            document.getElementById('currentTimeframe').textContent = '15m';
            document.getElementById('tradePlan').textContent = 'Mua → Giữ 15 phút → Take profit $118,500';
        });

        function updateTradingSignals(signal) {
            const signalPanel = document.querySelector('.signal-status');
            const actionText = document.querySelector('.action-text');
            const confidenceBadge = document.querySelector('.confidence-badge');
            const signalPrice = document.querySelector('.signal-price');
            const instructions = document.querySelector('.trading-instructions');
            
            if (!signalPanel || !actionText || !confidenceBadge) return;

            // Remove all signal classes
            signalPanel.classList.remove('signal-buy', 'signal-sell', 'signal-hold');
            
            // Set signal action
            let signalAction = signal.action || 'HOLD';
            let confidence = signal.confidence || 75;
            let currentPrice = signal.current_price || 116727;
            
            if (signalAction === 'BUY') {
                actionText.textContent = 'MUA NGAY';
                signalPanel.classList.add('signal-buy');
            } else if (signalAction === 'SELL') {
                actionText.textContent = 'BÁN NGAY';
                signalPanel.classList.add('signal-sell');
            } else {
                actionText.textContent = 'CHỜ THỜI CƠ';
                signalPanel.classList.add('signal-hold');
            }
            
            confidenceBadge.textContent = `${confidence}% TIN CẬY`;
            
            if (signalPrice) {
                signalPrice.textContent = `Giá hiện tại: $${currentPrice.toLocaleString()}`;
            }
            
            // Update instructions
            if (instructions && signal.instructions) {
                let instructionsHTML = '';
                signal.instructions.forEach(instruction => {
                    let icon = '📈';
                    if (instruction.includes('Stop Loss')) icon = '🛑';
                    else if (instruction.includes('Take Profit')) icon = '🎯';
                    else if (instruction.includes('Thời gian')) icon = '⏰';
                    
                    instructionsHTML += `
                        <div class="instruction-item">
                            <div class="instruction-icon">${icon}</div>
                            <div class="instruction-text">${instruction}</div>
                        </div>
                    `;
                });
                instructions.innerHTML = instructionsHTML;
            }
            
            // Enable/disable buttons based on signal
            updateActionButtons(signalAction);
        }

        function updateActionButtons(signalAction) {
            const buyBtn = document.querySelector('.btn-buy');
            const sellBtn = document.querySelector('.btn-sell');
            const cancelBtn = document.querySelector('.btn-cancel');
            
            // Reset all buttons
            [buyBtn, sellBtn, cancelBtn].forEach(btn => {
                if (btn) btn.classList.remove('btn-disabled');
            });
            
            // Disable buttons based on signal
            if (signalAction === 'BUY') {
                if (sellBtn) sellBtn.classList.add('btn-disabled');
            } else if (signalAction === 'SELL') {
                if (buyBtn) buyBtn.classList.add('btn-disabled');
            } else {
                // HOLD - disable buy and sell
                if (buyBtn) buyBtn.classList.add('btn-disabled');
                if (sellBtn) sellBtn.classList.add('btn-disabled');
            }
        }

        function executeBuy() {
            showAlert('🟢 LỆNH MUA đã được thực hiện!', 'success');
            socket.emit('trade_action', {
                action: 'BUY',
                timestamp: new Date().toISOString()
            });
        }

        function executeSell() {
            showAlert('🔴 LỆNH BÁN đã được thực hiện!', 'warning');
            socket.emit('trade_action', {
                action: 'SELL',
                timestamp: new Date().toISOString()
            });
        }

        function cancelOrder() {
            showAlert('⚪ LỆNH đã được HỦY!', 'info');
            socket.emit('trade_action', {
                action: 'CANCEL',
                timestamp: new Date().toISOString()
            });
        }

        function showAlert(message, type = 'info') {
            // Create alert element
            const alert = document.createElement('div');
            alert.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 25px;
                border-radius: 10px;
                color: white;
                font-weight: 600;
                z-index: 10000;
                animation: slideIn 0.3s ease;
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            `;
            
            switch(type) {
                case 'success':
                    alert.style.background = 'linear-gradient(45deg, #10b981, #059669)';
                    break;
                case 'warning':
                    alert.style.background = 'linear-gradient(45deg, #ef4444, #dc2626)';
                    break;
                case 'info':
                    alert.style.background = 'linear-gradient(45deg, #6b7280, #4b5563)';
                    break;
            }
            
            alert.textContent = message;
            document.body.appendChild(alert);
            
            // Remove after 3 seconds
            setTimeout(() => {
                alert.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }, 3000);
        }

        // Add CSS for alert animations
        const alertStyles = document.createElement('style');
        alertStyles.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(alertStyles);
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

def get_smart_ai_prediction():
    """Tạo dự đoán AI thông minh với timeframe"""
    current_price = bot_state['current_price']
    timeframe = bot_state.get('current_timeframe', '15m')
    
    # Get AI prediction
    prediction = ai_engine.predict_next_action(current_price, timeframe)
    
    # Generate trading plan
    plans = ai_engine.generate_trading_plan(
        current_price, 
        bot_state['capital'], 
        2.0  # 2% risk
    )
    
    current_plan = plans.get(timeframe, {})
    
    # Create trade plan text
    action_text = prediction['action']
    hold_time = prediction['timing']['minutes']
    
    if action_text == 'BUY':
        plan_text = f"Mua → Giữ {hold_time} phút → Take profit ${current_plan.get('take_profit', current_price * 1.02):.0f}"
    elif action_text == 'SELL':
        plan_text = f"Bán → Giữ {hold_time} phút → Take profit ${current_plan.get('take_profit', current_price * 0.98):.0f}"
    else:
        plan_text = f"Hold → Đánh giá lại sau {hold_time} phút → Chờ breakout"
    
    return {
        'signal': prediction['action'],
        'confidence': f"{prediction['confidence']*100:.0f}%",
        'target_price': f"${prediction['target_price']:.0f}",
        'analysis': prediction['analysis'],
        'timeframe': timeframe,
        'urgency': prediction['timing']['urgency'].title(),
        'next_signal_minutes': prediction['timing']['minutes'],
        'next_signal_seconds': prediction['timing']['seconds'],
        'trade_plan': plan_text,
        'market_session': prediction['market_session'],
        'stop_loss': f"${current_plan.get('stop_loss', current_price * 0.98):.0f}",
        'take_profit': f"${current_plan.get('take_profit', current_price * 1.02):.0f}",
        'position_size': f"${current_plan.get('position_size', 200):.0f}",
        'max_hold_time': f"{current_plan.get('max_hold_time', hold_time * 2)} phút"
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
    """API endpoint để lấy dữ liệu real-time với continuous analysis"""
    # Get continuous analysis data
    analysis_summary = continuous_analyzer.get_analysis_summary()
    
    return {
        'market': get_sample_market_data(),
        'ai': get_smart_ai_prediction(),
        'bot': get_sample_bot_status(),
        'continuous_analysis': analysis_summary,
        'strategy_plans': analysis_summary.get('plans_by_timeframe', {}),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/update_plans', methods=['POST'])
def update_plans():
    """Cập nhật kế hoạch thủ công"""
    plans = continuous_analyzer.get_current_plans()
    analysis = continuous_analyzer.get_analysis_summary()
    
    return {
        'plans_by_timeframe': analysis.get('plans_by_timeframe', {}),
        'best_timeframe': analysis.get('best_timeframe', '15m'),
        'best_plan': analysis.get('best_plan', ''),
        'confidence': analysis.get('confidence', '75%')
    }

@app.route('/change_timeframe', methods=['POST'])
def change_timeframe():
    """Thay đổi khung thời gian trading"""
    data = request.get_json()
    timeframe = data.get('timeframe', '15m')
    bot_state['current_timeframe'] = timeframe
    
    # Get new prediction for this timeframe
    return get_smart_ai_prediction()

@app.route('/start_bot', methods=['POST'])
def start_bot():
    bot_state['running'] = True
    
    # Start continuous AI analyzer
    continuous_analyzer.start_continuous_analysis()
    
    socketio.emit('bot_status', {'status': 'Bot đã khởi động'})
    return {'message': 'Bot và AI Analyzer đã được khởi động thành công!'}

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    bot_state['running'] = False
    
    # Stop continuous AI analyzer
    continuous_analyzer.stop_continuous_analysis()
    
    socketio.emit('bot_status', {'status': 'Bot đã dừng'})
    return {'message': 'Bot và AI Analyzer đã được dừng!'}

@socketio.on('trade_action')
def handle_trade_action(data):
    """Xử lý hành động trading từ client"""
    action = data.get('action', '')
    timestamp = data.get('timestamp', '')
    
    print(f"🎯 Trade Action Received: {action} at {timestamp}")
    
    # Log trade action
    trade_log = {
        'action': action,
        'timestamp': timestamp,
        'price': bot_state['current_price'],
        'status': 'executed'
    }
    
    # Emit confirmation back to client
    socketio.emit('trade_confirmation', {
        'action': action,
        'status': 'success',
        'message': f'Lệnh {action} đã được thực hiện thành công!',
        'timestamp': timestamp
    })
    
    # You can add actual trading logic here
    # For now, it's just logging and confirmation

@app.route('/refresh_data', methods=['POST'])
def refresh_data():
    # Emit new data to all connected clients
    socketio.emit('market_update', get_sample_market_data())
    socketio.emit('ai_prediction', get_smart_ai_prediction())
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
    emit('ai_prediction', get_smart_ai_prediction())
    emit('bot_status', get_sample_bot_status())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def background_data_emitter():
    """Gửi dữ liệu AI thông minh và continuous analysis"""
    while True:
        time.sleep(10)  # Every 10 seconds for real-time feeling
        if bot_state['running']:
            # Emit market data
            socketio.emit('market_update', get_sample_market_data())
            
            # Emit AI prediction
            socketio.emit('ai_prediction', get_smart_ai_prediction())
            
            # Emit bot status
            socketio.emit('bot_status', get_sample_bot_status())
            
            # Emit continuous analysis
            analysis_summary = continuous_analyzer.get_analysis_summary()
            if analysis_summary:
                socketio.emit('continuous_analysis', analysis_summary)
                
                # Emit strategy plans
                if analysis_summary.get('plans_by_timeframe'):
                    socketio.emit('strategy_plans', {
                        'plans_by_timeframe': analysis_summary['plans_by_timeframe'],
                        'best_timeframe': analysis_summary.get('best_timeframe', '15m'),
                        'best_plan': analysis_summary.get('best_plan', ''),
                        'confidence': analysis_summary.get('confidence', '75%')
                    })

def start_background_thread():
    """Khởi động thread nền"""
    thread = threading.Thread(target=background_data_emitter, daemon=True)
    thread.start()

if __name__ == '__main__':
    print("🚀 Starting Advanced Bitcoin AI Trading Dashboard...")
    print("📊 Dashboard: http://localhost:8082")
    print("💹 Real-time AI predictions with timeframe analysis")
    print("🤖 Smart trading engine with learning capabilities")
    print("💰 Multi-timeframe strategy analysis")
    print("🎯 Professional risk management tools")
    print("🧠 Continuous AI Analysis Engine")
    print("📋 Real-time strategy planning")
    print("🎯 Trading Signals: MUA/BÁN/HỦY rõ ràng")
    
    # Connect socketio to continuous analyzer
    continuous_analyzer.set_socketio(socketio)
    
    # Start continuous AI analyzer
    continuous_analyzer.start_continuous_analysis()
    
    start_background_thread()
    socketio.run(app, host='0.0.0.0', port=8082, debug=False)
