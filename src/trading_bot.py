"""
Unified Trading Bot - Combines all order types
"""
from .basic_bot import BasicBot
from .market_orders import MarketOrders
from .limit_orders import LimitOrders
from .advanced.stop_limit import StopLimitOrders
from .advanced.oco import OCOOrders
from .advanced.twap import TWAPOrders
from .advanced.grid import GridOrders


class TradingBot(MarketOrders, LimitOrders, StopLimitOrders, OCOOrders, TWAPOrders, GridOrders):
    """
    Unified trading bot with all order types
    
    Inherits from:
    - MarketOrders: Market buy/sell
    - LimitOrders: Limit buy/sell
    - StopLimitOrders: Stop-limit orders
    - OCOOrders: One-Cancels-the-Other orders
    - TWAPOrders: Time-Weighted Average Price orders
    - GridOrders: Grid trading orders
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """Initialize the unified trading bot"""
        BasicBot.__init__(self, api_key, api_secret, testnet)
    
    def get_account_balance(self) -> dict:
        """Get account balance information"""
        try:
            account = self.client.futures_account()
            return {
                'total_wallet_balance': account.get('totalWalletBalance', '0'),
                'available_balance': account.get('availableBalance', '0'),
                'total_unrealized_pnl': account.get('totalUnrealizedProfit', '0'),
                'total_margin_balance': account.get('totalMarginBalance', '0')
            }
        except Exception as e:
            self.log_error(e, "fetching account balance")
            return {}
    
    def get_position(self, symbol: str) -> dict:
        """Get current position for a symbol"""
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            if positions:
                pos = positions[0]
                return {
                    'symbol': pos.get('symbol'),
                    'position_amt': pos.get('positionAmt', '0'),
                    'entry_price': pos.get('entryPrice', '0'),
                    'unrealized_pnl': pos.get('unRealizedProfit', '0'),
                    'leverage': pos.get('leverage', '1')
                }
            return {}
        except Exception as e:
            self.log_error(e, f"fetching position for {symbol}")
            return {}
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            self.log_error(e, f"cancelling order {order_id}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """Cancel all open orders for a symbol"""
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"All orders cancelled for {symbol}")
            return True
        except Exception as e:
            self.log_error(e, f"cancelling all orders for {symbol}")
            return False
