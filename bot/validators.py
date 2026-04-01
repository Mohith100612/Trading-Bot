import re
from typing import Optional

def validate_symbol(symbol: str) -> str:
    """Validates the trading symbol matches expected format (e.g. BTCUSDT)"""
    symbol = symbol.upper()
    if not re.match(r"^[A-Z0-9]{3,20}$", symbol):
        raise ValueError(f"Invalid symbol format: '{symbol}'. Symbols usually look like 'BTCUSDT'.")
    return symbol

def validate_side(side: str) -> str:
    side = side.upper()
    if side not in ("BUY", "SELL"):
        raise ValueError("Side must be either 'BUY' or 'SELL'.")
    return side

def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper()
    if order_type not in ("MARKET", "LIMIT", "STOP_MARKET"):
        raise ValueError("Unsupported order type. Choose MARKET, LIMIT, or STOP_MARKET.")
    return order_type

def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    return quantity

def validate_price_requirements(order_type: str, price: Optional[float], stop_price: Optional[float]):
    order_type = order_type.upper()
    if order_type == "LIMIT" and price is None:
        raise ValueError("Limit orders require a 'price' value.")
    
    if order_type == "STOP_MARKET" and stop_price is None:
        raise ValueError("Stop Market orders require a 'stopPrice' value.")
