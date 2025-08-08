@echo off
echo 🚀 Starting Bitcoin AI Trading Bot...

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found! Please run setup.bat first
    pause
    exit /b 1
)

REM Create logs directory if not exists
if not exist logs mkdir logs

echo 📊 Bot is starting in DEMO mode...
echo 🌐 Dashboard will be available at http://localhost:5000
echo 🛑 Press Ctrl+C to stop the bot
echo.

REM Start the bot
python main.py

pause
