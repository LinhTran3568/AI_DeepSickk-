@echo off
echo 🤖 Bitcoin AI Trading Bot - Windows Setup
echo ========================================

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!
echo.

echo 🔧 Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys
)

echo.
echo 📁 Creating logs directory...
if not exist logs mkdir logs

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Available commands:
echo   - python main.py          : Run the trading bot
echo   - python dashboard.py     : Run the web dashboard
echo   - python -m pytest tests/ : Run tests
echo.

echo ⚠️  IMPORTANT: 
echo   1. Edit .env file with your real API keys
echo   2. Start with DEMO mode first
echo   3. Test thoroughly before live trading
echo.

pause
