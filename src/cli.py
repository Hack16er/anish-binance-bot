"""
CLI Interface for Binance Futures Trading Bot
"""
import argparse
import sys
import os
from dotenv import load_dotenv
import logging
from .trading_bot import TradingBot
from .time_sync import print_time_sync_info

# Load environment variables
load_dotenv()


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_order_result(order_result, order_type: str):
    """Print order result in a formatted way"""
    if order_result:
        print(f"\n{'='*60}")
        print(f"{order_type} Order Placed Successfully!")
        print(f"{'='*60}")
        if isinstance(order_result, dict):
            if 'orderId' in order_result:
                print(f"Order ID: {order_result['orderId']}")
                print(f"Symbol: {order_result.get('symbol', 'N/A')}")
                print(f"Side: {order_result.get('side', 'N/A')}")
                print(f"Type: {order_result.get('type', 'N/A')}")
                print(f"Quantity: {order_result.get('origQty', 'N/A')}")
                print(f"Status: {order_result.get('status', 'N/A')}")
            else:
                # Handle OCO or Grid orders
                for key, value in order_result.items():
                    if isinstance(value, list):
                        print(f"{key}: {len(value)} orders")
                    else:
                        print(f"{key}: {value}")
        elif isinstance(order_result, list):
            print(f"Total Orders: {len(order_result)}")
            for i, order in enumerate(order_result, 1):
                print(f"  Order {i}: ID {order.get('orderId', 'N/A')}")
        print(f"{'='*60}\n")
    else:
        print(f"\n[ERROR] Failed to place {order_type} order. Check logs for details.\n")


def main():
    """Main CLI entry point"""
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market order
  python -m src.cli market BUY BTCUSDT 0.01
  
  # Limit order
  python -m src.cli limit BUY BTCUSDT 0.01 50000
  
  # Stop-limit order
  python -m src.cli stop-limit SELL BTCUSDT 0.01 51000 50900
  
  # TWAP order
  python -m src.cli twap BUY BTCUSDT 0.1 60 10
  
  # Grid order
  python -m src.cli grid BTCUSDT 48000 52000 10 0.01
        """
    )
    
    # Global arguments
    parser.add_argument('--api-key', type=str, help='Binance API key (or set BINANCE_API_KEY env var)')
    parser.add_argument('--api-secret', type=str, help='Binance API secret (or set BINANCE_API_SECRET env var)')
    parser.add_argument('--mainnet', action='store_true', help='Use mainnet instead of testnet')
    
    subparsers = parser.add_subparsers(dest='command', help='Order type')
    
    # Market order
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    market_parser.add_argument('quantity', type=float, help='Order quantity')
    market_parser.add_argument('--reduce-only', action='store_true', help='Reduce only order')
    
    # Limit order
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    limit_parser.add_argument('quantity', type=float, help='Order quantity')
    limit_parser.add_argument('price', type=float, help='Limit price')
    limit_parser.add_argument('--time-in-force', choices=['GTC', 'IOC', 'FOK'], default='GTC', help='Time in force')
    limit_parser.add_argument('--reduce-only', action='store_true', help='Reduce only order')
    
    # Stop-limit order
    stop_limit_parser = subparsers.add_parser('stop-limit', help='Place a stop-limit order')
    stop_limit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    stop_limit_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    stop_limit_parser.add_argument('quantity', type=float, help='Order quantity')
    stop_limit_parser.add_argument('stop_price', type=float, help='Stop price')
    stop_limit_parser.add_argument('limit_price', type=float, help='Limit price')
    stop_limit_parser.add_argument('--reduce-only', action='store_true', help='Reduce only order')
    
    # OCO order
    oco_parser = subparsers.add_parser('oco', help='Place an OCO order (take-profit and stop-loss)')
    oco_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    oco_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    oco_parser.add_argument('quantity', type=float, help='Order quantity')
    oco_parser.add_argument('price', type=float, help='Current market price')
    oco_parser.add_argument('stop_price', type=float, help='Stop-loss price')
    oco_parser.add_argument('limit_price', type=float, help='Take-profit limit price')
    oco_parser.add_argument('--reduce-only', action='store_true', help='Reduce only order')
    
    # TWAP order
    twap_parser = subparsers.add_parser('twap', help='Place a TWAP order')
    twap_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    twap_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    twap_parser.add_argument('total_quantity', type=float, help='Total quantity to trade')
    twap_parser.add_argument('duration_minutes', type=int, help='Duration in minutes')
    twap_parser.add_argument('--intervals', type=int, default=10, help='Number of intervals (default: 10)')
    twap_parser.add_argument('--order-type', choices=['MARKET', 'LIMIT'], default='MARKET', help='Order type')
    
    # Grid order
    grid_parser = subparsers.add_parser('grid', help='Place grid orders')
    grid_parser.add_argument('symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    grid_parser.add_argument('lower_price', type=float, help='Lower price bound')
    grid_parser.add_argument('upper_price', type=float, help='Upper price bound')
    grid_parser.add_argument('grid_levels', type=int, help='Number of grid levels')
    grid_parser.add_argument('quantity_per_grid', type=float, help='Quantity per grid level')
    grid_parser.add_argument('--order-type', choices=['LIMIT', 'MARKET'], default='LIMIT', help='Order type')
    
    # Account info
    info_parser = subparsers.add_parser('info', help='Get account information')
    info_parser.add_argument('--symbol', type=str, help='Get position for specific symbol')
    
    # Cancel order
    cancel_parser = subparsers.add_parser('cancel', help='Cancel an order')
    cancel_parser.add_argument('symbol', type=str, help='Trading symbol')
    cancel_parser.add_argument('--order-id', type=int, help='Order ID to cancel')
    cancel_parser.add_argument('--all', action='store_true', help='Cancel all open orders')
    
    # Time sync check
    sync_parser = subparsers.add_parser('time-sync', help='Check time synchronization with Binance')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get API credentials
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("[ERROR] API key and secret are required!")
        print("Set them via --api-key/--api-secret flags or BINANCE_API_KEY/BINANCE_API_SECRET environment variables")
        sys.exit(1)
    
    # Initialize bot
    try:
        bot = TradingBot(api_key, api_secret, testnet=not args.mainnet)
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] Failed to initialize bot: {error_msg}\n")
        
        # Provide helpful error messages
        if "-1021" in error_msg or "Timestamp" in error_msg:
            print("[!] TIMESTAMP ERROR DETECTED")
            print("Your system clock is out of sync with Binance servers.")
            print("\nTo fix:")
            print("1. Windows: Open PowerShell as Administrator and run:")
            print("   w32tm /resync")
            print("2. Or sync your system clock manually:")
            print("   Settings > Time & Language > Date & time > Sync now")
            print("3. Check time sync status:")
            print("   python -m src.time_sync")
            print()
        elif "-1022" in error_msg or "Signature" in error_msg:
            print("[!] SIGNATURE ERROR DETECTED")
            print("Invalid API credentials or permissions.")
            print("\nTo fix:")
            print("1. Verify your API key and secret are correct")
            print("2. Make sure you're using TESTNET credentials (not mainnet)")
            print("3. Check API key permissions in Binance Testnet")
            print("4. Ensure API key is enabled and not restricted")
            print("5. Run: python test_credentials.py to diagnose")
            print()
        
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'market':
            if args.side == 'BUY':
                result = bot.market_buy(args.symbol, args.quantity, args.reduce_only)
            else:
                result = bot.market_sell(args.symbol, args.quantity, args.reduce_only)
            print_order_result(result, 'Market')
        
        elif args.command == 'limit':
            if args.side == 'BUY':
                result = bot.limit_buy(args.symbol, args.quantity, args.price, args.time_in_force, args.reduce_only)
            else:
                result = bot.limit_sell(args.symbol, args.quantity, args.price, args.time_in_force, args.reduce_only)
            print_order_result(result, 'Limit')
        
        elif args.command == 'stop-limit':
            if args.side == 'BUY':
                result = bot.stop_limit_buy(args.symbol, args.quantity, args.stop_price, args.limit_price, args.reduce_only)
            else:
                result = bot.stop_limit_sell(args.symbol, args.quantity, args.stop_price, args.limit_price, args.reduce_only)
            print_order_result(result, 'Stop-Limit')
        
        elif args.command == 'oco':
            result = bot.place_oco_order(
                args.symbol, args.side, args.quantity, args.price,
                args.stop_price, args.limit_price, args.reduce_only
            )
            print_order_result(result, 'OCO')
        
        elif args.command == 'twap':
            result = bot.place_twap_order(
                args.symbol, args.side, args.total_quantity,
                args.duration_minutes, args.intervals, args.order_type
            )
            print_order_result(result, 'TWAP')
        
        elif args.command == 'grid':
            result = bot.place_grid_orders(
                args.symbol, args.lower_price, args.upper_price,
                args.grid_levels, args.quantity_per_grid, args.order_type
            )
            print_order_result(result, 'Grid')
        
        elif args.command == 'info':
            balance = bot.get_account_balance()
            print(f"\n{'='*60}")
            print("Account Information")
            print(f"{'='*60}")
            for key, value in balance.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            
            if args.symbol:
                position = bot.get_position(args.symbol)
                if position:
                    print(f"\nPosition for {args.symbol}:")
                    for key, value in position.items():
                        print(f"  {key.replace('_', ' ').title()}: {value}")
            print(f"{'='*60}\n")
        
        elif args.command == 'cancel':
            if args.all:
                success = bot.cancel_all_orders(args.symbol)
                status = "[OK]" if success else "[ERROR]"
                print(f"{status} Cancel all orders: {'Success' if success else 'Failed'}")
            elif args.order_id:
                success = bot.cancel_order(args.symbol, args.order_id)
                status = "[OK]" if success else "[ERROR]"
                print(f"{status} Cancel order {args.order_id}: {'Success' if success else 'Failed'}")
            else:
                print("[ERROR] Specify --order-id or --all")
        
        elif args.command == 'time-sync':
            print_time_sync_info()
    
    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
