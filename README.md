Binance Futures Trading Bot

A comprehensive CLI-based trading bot for Binance USDT-M Futures that supports multiple order types with robust logging, validation, and error handling.

Features

Core Orders (Mandatory)
- ✅ **Market Orders** - Instant buy/sell at market price
- ✅ **Limit Orders** - Buy/sell at specified price

Advanced Orders (Bonus)
- ✅ **Stop-Limit Orders** - Trigger a limit order when stop price is hit
- ✅ **OCO Orders** - One-Cancels-the-Other (take-profit and stop-loss simultaneously)
- ✅ **TWAP Orders** - Time-Weighted Average Price (split large orders into smaller chunks)
- ✅ **Grid Orders** - Automated buy-low/sell-high within a price range

Additional Features
- ✅ Comprehensive input validation
- ✅ Structured logging to `bot.log`
- ✅ Error handling and recovery
- ✅ Account balance and position information
- ✅ Order cancellation support
- ✅ Testnet support (default)

Project Structure

```
Crypto/
├── src/
│   ├── __init__.py
│   ├── basic_bot.py          # Base bot class with Binance client
│   ├── market_orders.py      # Market order implementation
│   ├── limit_orders.py       # Limit order implementation
│   ├── trading_bot.py        # Unified bot class
│   ├── cli.py                # CLI interface
│   └── advanced/
│       ├── __init__.py
│       ├── stop_limit.py     # Stop-limit orders
│       ├── oco.py            # OCO orders
│       ├── twap.py           # TWAP orders
│       └── grid.py           # Grid orders
├── requirements.txt
├── README.md
└── bot.log                   # Log file (generated at runtime)
```

