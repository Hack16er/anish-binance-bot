"""
TWAP (Time-Weighted Average Price) - Split large orders into smaller chunks over time
"""
from typing import Dict, Any, Optional, List
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
from ..basic_bot import BasicBot


class TWAPOrders(BasicBot):
    """Handle TWAP orders for Binance Futures"""
    
    def place_twap_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        num_intervals: int = 10,
        order_type: str = 'MARKET'
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Place a TWAP order (split large order into smaller chunks)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            total_quantity: Total quantity to trade
            duration_minutes: Total duration in minutes
            num_intervals: Number of intervals to split the order (default: 10)
            order_type: 'MARKET' or 'LIMIT' (default: 'MARKET')
        
        Returns:
            List of order responses or None if failed
        """
        # Validation
        if not self.validate_symbol(symbol):
            self.logger.error(f"Invalid symbol: {symbol}")
            return None
        
        if side.upper() not in ['BUY', 'SELL']:
            self.logger.error(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
            return None
        
        if not self.validate_quantity(total_quantity):
            self.logger.error(f"Invalid total_quantity: {total_quantity}")
            return None
        
        if duration_minutes <= 0 or num_intervals <= 0:
            self.logger.error(f"Invalid duration_minutes or num_intervals")
            return None
        
        if order_type not in ['MARKET', 'LIMIT']:
            self.logger.error(f"Invalid order_type: {order_type}")
            return None
        
        # Calculate interval quantity and time
        interval_quantity = total_quantity / num_intervals
        interval_seconds = (duration_minutes * 60) / num_intervals
        
        # Format interval quantity
        formatted_interval_quantity = self.format_quantity(symbol, interval_quantity)
        if formatted_interval_quantity is None:
            self.logger.error(f"Failed to format quantity for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "TWAP",
            symbol,
            side.upper(),
            total_quantity=total_quantity,
            duration_minutes=duration_minutes,
            num_intervals=num_intervals,
            interval_quantity=formatted_interval_quantity,
            interval_seconds=interval_seconds
        )
        
        orders = []
        
        try:
            for i in range(num_intervals):
                self.logger.info(f"TWAP: Placing order {i+1}/{num_intervals}")
                
                if order_type == 'MARKET':
                    # Place market order
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side.upper(),
                        type='MARKET',
                        quantity=formatted_interval_quantity
                    )
                else:
                    # For limit orders, get current price
                    ticker = self.client.futures_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    
                    # Adjust price slightly for better fill probability
                    if side.upper() == 'BUY':
                        limit_price = current_price * 0.999  # Slightly below market
                    else:
                        limit_price = current_price * 1.001  # Slightly above market
                    
                    formatted_price = self.format_price(symbol, limit_price)
                    if formatted_price is None:
                        self.logger.error(f"Failed to format price for {symbol}")
                        continue
                    
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side.upper(),
                        type='LIMIT',
                        quantity=formatted_interval_quantity,
                        price=formatted_price,
                        timeInForce='IOC'  # Immediate or Cancel for better execution
                    )
                
                orders.append(order)
                self.logger.info(f"TWAP order {i+1} placed: {order.get('orderId')}")
                
                # Wait before next interval (except for last order)
                if i < num_intervals - 1:
                    time.sleep(interval_seconds)
            
            # Log response
            self.log_order_response({
                'total_orders': len(orders),
                'orders': orders
            })
            
            return orders
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing TWAP order for {symbol}")
            return orders if orders else None
        except BinanceOrderException as e:
            self.log_error(e, f"placing TWAP order for {symbol}")
            return orders if orders else None
        except Exception as e:
            self.log_error(e, f"placing TWAP order for {symbol}")
            return orders if orders else None
