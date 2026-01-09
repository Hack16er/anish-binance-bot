"""
OCO (One-Cancels-the-Other) Orders - Place take-profit and stop-loss simultaneously
"""
from typing import Dict, Any, Optional
from binance.exceptions import BinanceAPIException, BinanceOrderException
from ..basic_bot import BasicBot


class OCOOrders(BasicBot):
    """Handle OCO orders for Binance Futures"""
    
    def place_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Place an OCO order (take-profit and stop-loss)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Current market price (for reference)
            stop_price: Stop-loss price
            limit_price: Take-profit limit price
            reduce_only: If True, only reduce position (default: False)
        
        Returns:
            Dictionary with both order responses or None if failed
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
        
        if not all(self.validate_price(p) for p in [price, stop_price, limit_price]):
            self.logger.error(f"Invalid price values")
            return None
        
        # Format values
        formatted_quantity = self.format_quantity(symbol, quantity)
        formatted_stop_price = self.format_price(symbol, stop_price)
        formatted_limit_price = self.format_price(symbol, limit_price)
        
        if formatted_quantity is None or formatted_stop_price is None or formatted_limit_price is None:
            self.logger.error(f"Failed to format values for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "OCO",
            symbol,
            side.upper(),
            quantity=formatted_quantity,
            stop_price=formatted_stop_price,
            limit_price=formatted_limit_price,
            reduce_only=reduce_only
        )
        
        try:
            # For OCO, we place two orders:
            # 1. Stop-loss order (STOP type)
            # 2. Take-profit order (TAKE_PROFIT type)
            # Note: Binance Futures doesn't have native OCO, so we implement it by placing
            # two conditional orders and monitoring them
            
            orders = {}
            
            # Place stop-loss order
            stop_order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL' if side.upper() == 'BUY' else 'BUY',  # Opposite side for stop-loss
                type='STOP_MARKET',
                quantity=formatted_quantity,
                stopPrice=formatted_stop_price,
                reduceOnly=reduce_only
            )
            orders['stop_loss'] = stop_order
            self.logger.info(f"Stop-loss order placed: {stop_order.get('orderId')}")
            
            # Place take-profit order
            take_profit_order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL' if side.upper() == 'BUY' else 'BUY',  # Opposite side for take-profit
                type='TAKE_PROFIT_MARKET',
                quantity=formatted_quantity,
                stopPrice=formatted_limit_price,
                reduceOnly=reduce_only
            )
            orders['take_profit'] = take_profit_order
            self.logger.info(f"Take-profit order placed: {take_profit_order.get('orderId')}")
            
            # Log response
            self.log_order_response(orders)
            
            return orders
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing OCO order for {symbol}")
            # Try to cancel any partially placed orders
            self._cancel_oco_orders(symbol, orders if 'orders' in locals() else {})
            return None
        except BinanceOrderException as e:
            self.log_error(e, f"placing OCO order for {symbol}")
            self._cancel_oco_orders(symbol, orders if 'orders' in locals() else {})
            return None
        except Exception as e:
            self.log_error(e, f"placing OCO order for {symbol}")
            self._cancel_oco_orders(symbol, orders if 'orders' in locals() else {})
            return None
    
    def _cancel_oco_orders(self, symbol: str, orders: Dict[str, Any]):
        """Cancel orders if OCO placement partially failed"""
        for order_type, order in orders.items():
            try:
                if order and 'orderId' in order:
                    self.client.futures_cancel_order(symbol=symbol, orderId=order['orderId'])
                    self.logger.info(f"Cancelled {order_type} order: {order['orderId']}")
            except Exception as e:
                self.logger.error(f"Failed to cancel {order_type} order: {e}")
