<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Bitcoin AI Trading Bot - Copilot Instructions

## Project Context
This is an AI-powered Bitcoin trading bot that:
- Uses DeepSeek API for market analysis and prediction
- Implements technical analysis and risk management
- Provides real-time trading signals for cryptocurrency markets
- Similar to Exness platform functionality but focused on Bitcoin

## Development Guidelines

### Code Style
- Use Python 3.9+ features
- Follow PEP 8 standards
- Implement comprehensive error handling
- Use type hints for all functions
- Add detailed docstrings for all modules

### AI/ML Focus
- Integrate DeepSeek API for market sentiment analysis
- Implement multiple timeframe analysis (1m, 5m, 15m, 1h, 4h, 1d)
- Use technical indicators for signal generation
- Implement backtesting for strategy validation

### Trading Logic
- Focus on Bitcoin (BTC/USDT) pairs
- Implement risk management (stop loss, take profit)
- Use position sizing based on account percentage
- Implement real-time market data processing

### Security
- Never hardcode API keys in source code
- Use environment variables for sensitive data
- Implement rate limiting for API calls
- Add input validation for all user inputs

### Architecture
- Use modular design with clear separation of concerns
- Implement async operations for real-time data
- Use SQLite for local data storage
- Create responsive web dashboard with Flask/Dash

### Testing
- Write unit tests for all trading logic
- Implement mock trading for safe testing
- Use demo accounts before live trading
- Validate all API integrations

### Monitoring
- Implement comprehensive logging
- Add performance metrics tracking
- Create alerts for system errors
- Monitor API rate limits and usage
