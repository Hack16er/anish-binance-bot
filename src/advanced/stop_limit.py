"""
Stop-Limit Orders - Trigger a limit order when stop price is hit
"""
from typing import Dict, Any, Optional
from binance.exceptions import BinanceAPIException, BinanceOrderException
from ..basic_bot import BasicBot


class StopLimitOrders(BasicBot):
    """Handle stop-limit orders for Binance Futures"""
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Place a stop-limit order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            stop_price: Stop price that triggers the limit order
            limit_price: Limit price for the order
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
        
        if not self.validate_price(stop_price) or not self.validate_price(limit_price):
            self.logger.error(f"Invalid stop_price or limit_price")
            return None
        
        # For BUY stop-limit: stop_price should be above current price
        # For SELL stop-limit: stop_price should be below current price
        # (This is a basic check, actual validation depends on market conditions)
        
        # Format values
        formatted_quantity = self.format_quantity(symbol, quantity)
        formatted_stop_price = self.format_price(symbol, stop_price)
        formatted_limit_price = self.format_price(symbol, limit_price)
        
        if formatted_quantity is None or formatted_stop_price is None or formatted_limit_price is None:
            self.logger.error(f"Failed to format values for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "STOP_LIMIT",
            symbol,
            side.upper(),
            quantity=formatted_quantity,
            stop_price=formatted_stop_price,
            limit_price=formatted_limit_price,
            reduce_only=reduce_only
        )
        
        try:
            # Place stop-limit order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='STOP',
                quantity=formatted_quantity,
                stopPrice=formatted_stop_price,
                price=formatted_limit_price,
                timeInForce='GTC',
                reduceOnly=reduce_only
            )
            
            # Log response
            self.log_order_response(order)
            
            return order
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing stop-limit {side} order for {symbol}")
            return None
        except BinanceOrderException as e:
            self.log_error(e, f"placing stop-limit {side} order for {symbol}")
            return None
        except Exception as e:
            self.log_error(e, f"placing stop-limit {side} order for {symbol}")
            return None
    
    def stop_limit_buy(
        self,
        symbol: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Place a stop-limit buy order"""
        return self.place_stop_limit_order(symbol, 'BUY', quantity, stop_price, limit_price, reduce_only)
    
    def stop_limit_sell(
        self,
        symbol: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Place a stop-limit sell order"""
        return self.place_stop_limit_order(symbol, 'SELL', quantity, stop_price, limit_price, reduce_only)
