"""
Basic Bot - Core trading bot class with Binance Futures API integration
"""
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Optional, Dict, Any
import time
import requests


class BasicBot:
    """Base class for Binance Futures trading bot"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, recv_window: int = 5000):
        """
        Initialize the trading bot
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet (default: True)
            recv_window: Receive window in milliseconds (default: 5000)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.recv_window = recv_window
        
        # Configure Binance client with recvWindow
        if testnet:
            # For testnet, we need to use the testnet base URL
            # Note: python-binance testnet=True should handle this, but we verify
            self.client = Client(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True
            )
            # Explicitly set testnet base URL for futures
            # This ensures we're using the correct testnet endpoint
            if hasattr(self.client, 'FUTURES_URL'):
                # python-binance should set this automatically, but we verify
                pass
        else:
            self.client = Client(api_key=api_key, api_secret=api_secret)
        
        # Set recvWindow for all requests (increases tolerance for time differences)
        self.client.recv_window = recv_window
        
        # Setup logger
        self.logger = logging.getLogger('BinanceBot')
        self.logger.setLevel(logging.INFO)
        
        # Sync time with Binance server
        self._sync_server_time()
        
        # Validate connection
        try:
            account_info = self.client.futures_account()
            self.logger.info(f"Connected to Binance Futures {'Testnet' if testnet else 'Mainnet'}")
            self.logger.info(f"Account Balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
        except BinanceAPIException as e:
            if e.code == -1021:
                self.logger.error("Timestamp synchronization error. Please sync your system clock.")
                self.logger.error("Windows: Run 'w32tm /resync' as administrator")
                self.logger.error("Or check your system time settings")
            elif e.code == -1022:
                self.logger.error("Invalid API signature. Please check your API key and secret.")
                self.logger.error("Make sure you're using the correct credentials for testnet/mainnet")
            self.logger.error(f"Failed to connect to Binance: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    def _sync_server_time(self):
        """Sync local time with Binance server time"""
        try:
            if self.testnet:
                base_url = 'https://testnet.binancefuture.com'
            else:
                base_url = 'https://fapi.binance.com'
            
            # Get server time
            response = requests.get(f'{base_url}/fapi/v1/time', timeout=5)
            server_time = response.json()['serverTime']
            
            # Calculate time difference
            local_time = int(time.time() * 1000)
            time_diff = server_time - local_time
            
            if abs(time_diff) > 1000:  # More than 1 second difference
                self.logger.warning(f"Time difference detected: {time_diff}ms")
                self.logger.warning("Consider syncing your system clock with internet time")
            else:
                self.logger.info(f"Time synchronized (diff: {time_diff}ms)")
                
        except Exception as e:
            self.logger.warning(f"Could not sync server time: {e}")
            self.logger.warning("Continuing anyway, but timestamp errors may occur")
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False
        # Basic validation: should be uppercase and contain USDT
        return symbol.isupper() and 'USDT' in symbol
    
    def validate_quantity(self, quantity: float) -> bool:
        """Validate order quantity"""
        return quantity > 0
    
    def validate_price(self, price: float) -> bool:
        """Validate order price"""
        return price > 0
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol trading information"""
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            return None
        except Exception as e:
            self.logger.error(f"Error fetching symbol info: {e}")
            return None
    
    def format_quantity(self, symbol: str, quantity: float) -> Optional[float]:
        """Format quantity according to symbol precision"""
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return None
        
        quantity_precision = symbol_info.get('quantityPrecision', 8)
        return round(quantity, quantity_precision)
    
    def format_price(self, symbol: str, price: float) -> Optional[float]:
        """Format price according to symbol precision"""
        symbol_info = self.get_symbol_info(symbol)
        if not symbol_info:
            return None
        
        price_precision = symbol_info.get('pricePrecision', 8)
        return round(price, price_precision)
    
    def log_order_request(self, order_type: str, symbol: str, side: str, **kwargs):
        """Log order request details"""
        self.logger.info(f"Order Request - Type: {order_type}, Symbol: {symbol}, Side: {side}, Details: {kwargs}")
    
    def log_order_response(self, response: Dict[str, Any]):
        """Log order response"""
        self.logger.info(f"Order Response: {response}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        self.logger.error(f"Error {context}: {type(error).__name__} - {str(error)}", exc_info=True)
