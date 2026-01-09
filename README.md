Binance Futures Trading Bot (USDT-M Testnet)

A CLI-based trading bot built in Python for Binance USDT-M Futures Testnet.
The project focuses on clean structure, reproducibility, and safe order execution using the official Binance Futures REST API.

This bot was developed as part of a technical evaluation task and is designed to be easy to run, inspect, and extend.

Key Features
Core Requirements

Market orders (BUY / SELL)

Limit orders (BUY / SELL)

Binance Futures USDT-M Testnet support

Command-line interface with input validation

Clear order execution output

Centralized logging and error handling

Bonus Implementations

Stop-Limit orders

OCO orders (take-profit + stop-loss)

TWAP execution (order splitting)

Grid trading strategy

Account and position inspection

Order cancellation support

All trading is performed on testnet by default to avoid real fund risk.

Project Structure
Crypto/
├── src/
│   ├── __init__.py
│   ├── basic_bot.py        # Base Binance Futures client
│   ├── trading_bot.py     # Unified trading logic
│   ├── cli.py              # CLI entry point
│   ├── market_orders.py
│   ├── limit_orders.py
│   └── advanced/
│       ├── stop_limit.py
│       ├── oco.py
│       ├── twap.py
│       └── grid.py
├── requirements.txt
├── README.md
└── bot.log                 # Generated at runtime

API Setup Instructions (Reproducibility)
1. Create Binance Futures Testnet Account

Visit: https://testnet.binancefuture.com

Log in using a Binance account

Enable USDT-M Futures

Use the testnet faucet to obtain test USDT

2. Generate API Credentials

Go to API Management

Create a new API key

Enable Futures Trading

Do not enable withdrawals

Save the API key and secret securely

Environment Setup
Prerequisites

Python 3.7+

Internet connection

Binance Futures Testnet API credentials

Install Dependencies
pip install -r requirements.txt

Configure API Credentials
Recommended: Environment Variables

Windows (PowerShell):

setx BINANCE_API_KEY "your_api_key"
setx BINANCE_API_SECRET "your_api_secret"

Restart the terminal after setting variables.

How to Run the Bot

All commands are executed from the project root.

Market Order
python -m src.cli market BUY BTCUSDT 0.01

Limit Order
python -m src.cli limit SELL BTCUSDT 0.01 51000

Stop-Limit Order
python -m src.cli stop-limit SELL BTCUSDT 0.01 51000 50900

OCO Order
python -m src.cli oco BUY BTCUSDT 0.01 50000 49000 52000

TWAP Order
python -m src.cli twap BUY BTCUSDT 0.1 60 --intervals 10

Grid Strategy
python -m src.cli grid BTCUSDT 48000 52000 10 0.01

Utility Commands
Account Information
python -m src.cli info
python -m src.cli info --symbol BTCUSDT

Cancel Orders
python -m src.cli cancel BTCUSDT --order-id 123456
python -m src.cli cancel BTCUSDT --all

Testnet vs Mainnet

The bot uses Binance Testnet by default.

To run on mainnet:

python -m src.cli market BUY BTCUSDT 0.01 --mainnet


Logging

All API requests, responses, and errors are logged to:

bot.log


Logs include:

Order payloads

Execution results

API errors

Validation failures

This makes debugging and review straightforward.

Input Validation

The bot validates:

Trading symbol format (BTCUSDT)

Order side (BUY / SELL)

Quantity and price values

Time-in-force parameters

Supported order types

Invalid inputs fail early with clear messages.

Error Handling

API errors are caught and logged

Network issues are handled gracefully

Execution failures return readable output

No silent failures

Testing Notes

Before submission or review:

Use testnet credentials only

Verify order placement

Check bot.log for correctness

Confirm balance updates on testnet UI

References

Binance Futures API:
https://binance-docs.github.io/apidocs/futures/en/

Binance Futures Testnet:
https://testnet.binancefuture.com/