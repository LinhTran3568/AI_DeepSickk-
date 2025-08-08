#!/bin/bash

echo "🤖 Bitcoin AI Trading Bot - Setup"
echo "=================================="

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

echo "🔧 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
fi

echo ""
echo "📁 Creating logs directory..."
mkdir -p logs

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Available commands:"
echo "  - python main.py          : Run the trading bot"
echo "  - python dashboard.py     : Run the web dashboard"  
echo "  - python -m pytest tests/ : Run tests"
echo ""

echo "⚠️  IMPORTANT:"
echo "  1. Edit .env file with your real API keys"
echo "  2. Start with DEMO mode first"
echo "  3. Test thoroughly before live trading"
echo ""
