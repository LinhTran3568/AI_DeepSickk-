@echo off
echo 🖥️ Starting Bitcoin Trading Bot Dashboard...

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found! Please run setup.bat first
    pause
    exit /b 1
)

echo 📊 Dashboard starting...
echo 🌐 Open your browser to: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the dashboard
echo.

REM Start the dashboard
python dashboard.py

pause
