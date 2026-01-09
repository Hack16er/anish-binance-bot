"""
Market Orders - Implementation for market buy/sell orders
"""
import logging
from typing import Dict, Any, Optional
from binance.exceptions import BinanceAPIException, BinanceOrderException
from .basic_bot import BasicBot


class MarketOrders(BasicBot):
    """Handle market orders for Binance Futures"""
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            reduce_only: If True, only reduce position (default: False)
        
        Returns:
            Order response dictionary or None if failed
        """
        # Validation
        if not self.validate_symbol(symbol):
            self.logger.error(f"Invalid symbol: {symbol}")
            return None
        
        if side.upper() not in ['BUY', 'SELL']:
            self.logger.error(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
            return None
        
        if not self.validate_quantity(quantity):
            self.logger.error(f"Invalid quantity: {quantity}")
            return None
        
        # Format quantity
        formatted_quantity = self.format_quantity(symbol, quantity)
        if formatted_quantity is None:
            self.logger.error(f"Failed to format quantity for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "MARKET",
            symbol,
            side.upper(),
            quantity=formatted_quantity,
            reduce_only=reduce_only
        )
        
        try:
            # Place market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=formatted_quantity,
                reduceOnly=reduce_only
            )
            
            # Log response
            self.log_order_response(order)
            
            return order
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing market {side} order for {symbol}")
            return None
        except BinanceOrderException as e:
            self.log_error(e, f"placing market {side} order for {symbol}")
            return None
        except Exception as e:
            self.log_error(e, f"placing market {side} order for {symbol}")
            return None
    
    def market_buy(self, symbol: str, quantity: float, reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """Place a market buy order"""
        return self.place_market_order(symbol, 'BUY', quantity, reduce_only)
    
    def market_sell(self, symbol: str, quantity: float, reduce_only: bool = False) -> Optional[Dict[str, Any]]:
        """Place a market sell order"""
        return self.place_market_order(symbol, 'SELL', quantity, reduce_only)
