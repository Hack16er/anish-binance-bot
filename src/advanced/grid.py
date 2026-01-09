"""
Grid Orders - Automated buy-low/sell-high within a price range
"""
from typing import Dict, Any, Optional, List
from binance.exceptions import BinanceAPIException, BinanceOrderException
from ..basic_bot import BasicBot


class GridOrders(BasicBot):
    """Handle grid trading orders for Binance Futures"""
    
    def place_grid_orders(
        self,
        symbol: str,
        lower_price: float,
        upper_price: float,
        grid_levels: int,
        quantity_per_grid: float,
        order_type: str = 'LIMIT'
    ) -> Optional[Dict[str, Any]]:
        """
        Place grid orders (buy-low/sell-high strategy)
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            lower_price: Lower bound of price range
            upper_price: Upper bound of price range
            grid_levels: Number of grid levels
            quantity_per_grid: Quantity per grid level
            order_type: 'LIMIT' or 'MARKET' (default: 'LIMIT')
        
        Returns:
            Dictionary with buy and sell orders or None if failed
        """
        # Validation
        if not self.validate_symbol(symbol):
            self.logger.error(f"Invalid symbol: {symbol}")
            return None
        
        if not self.validate_price(lower_price) or not self.validate_price(upper_price):
            self.logger.error(f"Invalid price range")
            return None
        
        if lower_price >= upper_price:
            self.logger.error(f"lower_price must be less than upper_price")
            return None
        
        if grid_levels <= 0:
            self.logger.error(f"grid_levels must be positive")
            return None
        
        if not self.validate_quantity(quantity_per_grid):
            self.logger.error(f"Invalid quantity_per_grid: {quantity_per_grid}")
            return None
        
        if order_type not in ['LIMIT', 'MARKET']:
            self.logger.error(f"Invalid order_type: {order_type}")
            return None
        
        # Calculate grid prices
        price_step = (upper_price - lower_price) / grid_levels
        grid_prices = [lower_price + i * price_step for i in range(grid_levels + 1)]
        
        # Format values
        formatted_quantity = self.format_quantity(symbol, quantity_per_grid)
        if formatted_quantity is None:
            self.logger.error(f"Failed to format quantity for {symbol}")
            return None
        
        # Log request
        self.log_order_request(
            "GRID",
            symbol,
            "BOTH",
            lower_price=lower_price,
            upper_price=upper_price,
            grid_levels=grid_levels,
            quantity_per_grid=formatted_quantity
        )
        
        buy_orders = []
        sell_orders = []
        
        try:
            # Get current market price
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Place buy orders below current price
            for price in grid_prices:
                if price < current_price:
                    formatted_price = self.format_price(symbol, price)
                    if formatted_price is None:
                        continue
                    
                    if order_type == 'LIMIT':
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='BUY',
                            type='LIMIT',
                            quantity=formatted_quantity,
                            price=formatted_price,
                            timeInForce='GTC'
                        )
                    else:
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='BUY',
                            type='MARKET',
                            quantity=formatted_quantity
                        )
                    
                    buy_orders.append(order)
                    self.logger.info(f"Grid BUY order placed at {formatted_price}: {order.get('orderId')}")
            
            # Place sell orders above current price
            for price in grid_prices:
                if price > current_price:
                    formatted_price = self.format_price(symbol, price)
                    if formatted_price is None:
                        continue
                    
                    if order_type == 'LIMIT':
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='SELL',
                            type='LIMIT',
                            quantity=formatted_quantity,
                            price=formatted_price,
                            timeInForce='GTC'
                        )
                    else:
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='SELL',
                            type='MARKET',
                            quantity=formatted_quantity
                        )
                    
                    sell_orders.append(order)
                    self.logger.info(f"Grid SELL order placed at {formatted_price}: {order.get('orderId')}")
            
            result = {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders,
                'total_buy_orders': len(buy_orders),
                'total_sell_orders': len(sell_orders)
            }
            
            # Log response
            self.log_order_response(result)
            
            return result
            
        except BinanceAPIException as e:
            self.log_error(e, f"placing grid orders for {symbol}")
            return {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders
            } if (buy_orders or sell_orders) else None
        except BinanceOrderException as e:
            self.log_error(e, f"placing grid orders for {symbol}")
            return {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders
            } if (buy_orders or sell_orders) else None
        except Exception as e:
            self.log_error(e, f"placing grid orders for {symbol}")
            return {
                'buy_orders': buy_orders,
                'sell_orders': sell_orders
            } if (buy_orders or sell_orders) else None
