"""
Limit Orders - Implementation for limit buy/sell orders
"""
import logging
from typing import Dict, Any, Optional
from binance.exceptions import BinanceAPIException, BinanceOrderException
from .basic_bot import BasicBot


class LimitOrders(BasicBot):
    """Handle limit orders for Binance Futures"""
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC',
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: 'GTC' (Good Till Cancel), 'IOC' (Immediate or Cancel), 'FOK' (Fill or Kill)
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
        
        if not self.validate_price(price):
            self.logger.error(f"Invalid price: {price}")
            return None
        
        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            self.logger.error(f"Invalid time_in_force: {time_in_force}")
            return None
        
        # Format quantity and price
        formatted_quantity = self.format_quantity(symbol, quantity)
        formatted_price = self.format_price(symbol, price)
        
        if formatted_quantity is None or formatted_price is None:
            self.logger.error(f"Failed to format quantity/price for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "LIMIT",
            symbol,
            side.upper(),
            quantity=formatted_quantity,
            price=formatted_price,
            time_in_force=time_in_force,
            reduce_only=reduce_only
        )
        
        try:
            # Place limit order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='LIMIT',
                quantity=formatted_quantity,
                price=formatted_price,
                timeInForce=time_in_force,
                reduceOnly=reduce_only
            )
            
            # Log response
            self.log_order_response(order)
            
            return order
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing limit {side} order for {symbol}")
            return None
        except BinanceOrderException as e:
            self.log_error(e, f"placing limit {side} order for {symbol}")
            return None
        except Exception as e:
            self.log_error(e, f"placing limit {side} order for {symbol}")
            return None
    
    def limit_buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC',
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Place a limit buy order"""
        return self.place_limit_order(symbol, 'BUY', quantity, price, time_in_force, reduce_only)
    
    def limit_sell(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC',
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Place a limit sell order"""
        return self.place_limit_order(symbol, 'SELL', quantity, price, time_in_force, reduce_only)
