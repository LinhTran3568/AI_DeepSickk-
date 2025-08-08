# 🤖 Bitcoin AI Trading Bot

## Tổng quan
Hệ thống AI trading bot tự động cho Bitcoin, sử dụng DeepSeek API để phân tích thị trường và đưa ra quyết định giao dịch thông minh.

## ✨ Tính năng chính

### 🧠 AI Dự đoán xu hướng
- **DeepSeek API Integration**: Phân tích sâu xu hướng thị trường Bitcoin
- **Multiple Timeframes**: Phân tích đa khung thời gian (1m, 5m, 15m, 1h, 4h, 1d)
- **Pattern Recognition**: Nhận diện các pattern biểu đồ tự động
- **Market Sentiment**: Đánh giá tâm lý thị trường real-time

### 📊 Phân tích kỹ thuật
- **50+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages...
- **Support/Resistance**: Tự động xác định mức hỗ trợ và kháng cự
- **Volume Analysis**: Phân tích khối lượng giao dịch
- **Multi-timeframe Confluence**: Kết hợp tín hiệu từ nhiều khung thời gian

### 💰 Quản lý vốn & Rủi ro
- **Position Sizing**: Tính toán quy mô vị thế dựa trên % tài khoản
- **Stop Loss/Take Profit**: Tự động cắt lỗ và chốt lời
- **Risk/Reward Ratio**: Đảm bảo tỷ lệ rủi ro/lợi nhuận tối ưu
- **Drawdown Protection**: Bảo vệ tài khoản khỏi rút vốn quá mức

### 🎯 Tín hiệu giao dịch
- **AI + Technical Fusion**: Kết hợp AI analysis và technical signals
- **Confidence Scoring**: Đánh giá độ tin cậy của từng tín hiệu
- **Real-time Alerts**: Thông báo ngay lập tức khi có tín hiệu
- **Backtesting**: Kiểm tra hiệu quả trên dữ liệu lịch sử

### 🖥️ Dashboard Web
- **Real-time Charts**: Biểu đồ giá Bitcoin live
- **P&L Tracking**: Theo dõi lãi/lỗ chi tiết
- **Performance Analytics**: Thống kê hiệu suất giao dịch
- **Bot Control**: Điều khiển bot từ xa qua web

## 🚀 Cài đặt nhanh

### Yêu cầu hệ thống
- Python 3.9 hoặc cao hơn
- Windows 10/11 hoặc Linux/macOS
- Kết nối Internet ổn định
- 4GB RAM (khuyến nghị 8GB)

### 1. Clone và cài đặt
```bash
# Clone repository
git clone <repository-url>
cd API-key

# Chạy script setup (Windows)
setup.bat

# Hoặc Linux/macOS
chmod +x setup.sh
./setup.sh
```

### 2. Cấu hình API Keys
```bash
# Copy file cấu hình
cp .env.example .env

# Chỉnh sửa file .env với API keys của bạn
notepad .env  # Windows
nano .env     # Linux/macOS
```

### 3. Chạy Bot
```bash
# Chạy trading bot
python main.py

# Hoặc sử dụng script (Windows)
run_bot.bat

# Chạy dashboard (cửa sổ mới)
python dashboard.py
# Hoặc
run_dashboard.bat
```

## 📋 Cấu hình Bot

### API Keys cần thiết
```env
# DeepSeek API (Đã có)
DEEPSEEK_API_KEY=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

# Exchange API (Demo/Live)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=True  # True cho demo, False cho live

# Bot Settings
BOT_MODE=demo  # demo hoặc live
TRADING_PAIR=BTC/USDT
INITIAL_BALANCE=10000
```

### Cài đặt Risk Management
```env
MAX_POSITION_SIZE=5      # % tài khoản tối đa cho 1 lệnh
STOP_LOSS_PERCENT=2      # % cắt lỗ
TAKE_PROFIT_PERCENT=4    # % chốt lời
MAX_DAILY_TRADES=10      # Số lệnh tối đa mỗi ngày
```

## 🎮 Demo Mode (Khuyến nghị)
Bot mặc định chạy ở **Demo Mode** - an toàn để test:
- Không dùng tiền thật
- Mô phỏng giao dịch với $10,000 ảo
- Tất cả tính năng hoạt động đầy đủ
- Kiểm tra chiến lược trước khi live

## 🖥️ Dashboard Web
Truy cập dashboard tại: `http://localhost:5000`

### Tính năng Dashboard:
- **Real-time Bitcoin Chart**: Biểu đồ giá live với indicators
- **Bot Controls**: Start/Stop bot từ xa
- **Live Signals**: Xem tín hiệu giao dịch real-time
- **Trade History**: Lịch sử các giao dịch
- **Performance Metrics**: Thống kê hiệu suất
- **Balance Tracking**: Theo dõi số dư tài khoản

## 📊 Cấu trúc Project

```
bitcoin_ai_bot/
├── main.py                 # Entry point chính
├── dashboard.py            # Web dashboard
├── requirements.txt        # Python dependencies
├── .env                    # Cấu hình (tạo từ .env.example)
├── setup.bat/sh           # Script cài đặt
├── run_bot.bat            # Script chạy bot (Windows)
├── run_dashboard.bat      # Script chạy dashboard (Windows)
│
├── config/                # Cấu hình
│   ├── settings.py        # Cài đặt bot
│   └── __init__.py
│
├── ai_engine/             # AI Engine
│   ├── deepseek_client.py # DeepSeek API client
│   └── __init__.py
│
├── trading/               # Trading Logic
│   ├── exchange.py        # Exchange management
│   ├── signals.py         # Signal generation
│   ├── risk_manager.py    # Risk management
│   └── __init__.py
│
├── data/                  # Data Management
│   ├── collector.py       # Market data collection
│   ├── database.py        # Database operations
│   └── __init__.py
│
├── utils/                 # Utilities
│   ├── logger.py          # Logging system
│   ├── notifications.py   # Alert system
│   └── __init__.py
│
├── dashboard/             # Web Dashboard
│   └── templates/
│       └── index.html     # Dashboard UI
│
├── tests/                 # Test Cases
│   ├── test_bot.py        # Bot tests
│   └── __init__.py
│
└── logs/                  # Log files (tự tạo)
```

## 🧪 Testing

```bash
# Chạy tất cả tests
python -m pytest tests/ -v

# Test specific component
python -m pytest tests/test_bot.py::TestExchangeManager -v

# Test với coverage
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html
```

## 📈 Chiến lược Trading

### AI Analysis (60% weight)
- DeepSeek API phân tích market sentiment
- Pattern recognition từ historical data
- Trend prediction với confidence scoring

### Technical Analysis (40% weight)
- RSI: Oversold/Overbought signals
- MACD: Momentum và trend changes
- Moving Averages: Trend confirmation
- Support/Resistance: Entry/Exit levels
- Volume: Signal confirmation

### Combined Signals
- Chỉ trade khi cả AI và Technical đều confirm
- Minimum confidence: 70%
- Risk/Reward ratio tối thiểu: 1:1.5

## ⚠️ Cảnh báo An toàn

### 🚨 Trading Risks
- **High Risk**: Cryptocurrency trading có rủi ro cao
- **Start Small**: Bắt đầu với số tiền nhỏ
- **Demo First**: Luôn test ở demo mode trước
- **No Guarantee**: Không đảm bảo lợi nhuận

### 🔒 Security
- **Never Share**: Không chia sẻ API keys
- **Secure Storage**: Lưu trữ keys an toàn
- **Regular Updates**: Cập nhật bot thường xuyên
- **Monitor Always**: Luôn theo dõi bot hoạt động

## 🛠️ Troubleshooting

### Lỗi thường gặp:

**1. Import Error**
```bash
# Cài đặt lại dependencies
pip install -r requirements.txt --force-reinstall
```

**2. API Key Error**
```bash
# Kiểm tra file .env
cat .env  # Linux/macOS
type .env  # Windows

# Đảm bảo API key đúng format
```

**3. Connection Error**
```bash
# Kiểm tra internet
ping api.binance.com

# Kiểm tra firewall/antivirus
```

**4. Permission Error**
```bash
# Chạy với quyền admin (Windows)
# Hoặc chmod +x cho Linux/macOS
```

## 📞 Support

### 🐛 Bug Report
- Mở issue trên GitHub
- Cung cấp log files từ thư mục `logs/`
- Mô tả chi tiết lỗi và steps reproduce

### 💡 Feature Request
- Đề xuất tính năng mới
- Thảo luận implementation
- Contribute code nếu có thể

### 📚 Documentation
- Wiki: Chi tiết các tính năng
- Examples: Ví dụ sử dụng
- API Reference: Tài liệu API

## 🔄 Updates

Bot được cập nhật thường xuyên với:
- Cải thiện AI models
- Thêm technical indicators
- Bug fixes và optimizations
- Security updates

```bash
# Update bot
git pull origin main
pip install -r requirements.txt --upgrade
```

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết chi tiết.

## 🙏 Disclaimer

**Đây là phần mềm giáo dục/nghiên cứu. Không phải lời khuyên đầu tư. Luôn thực hiện nghiên cứu riêng và chỉ đầu tư số tiền bạn có thể chấp nhận mất.**

---

**🤖 Happy Trading với Bitcoin AI Bot! 🚀**
# AI_DeepSickk-
