from typing import Dict, Any, Optional
from bot.client import BinanceFuturesClient
from bot.logger import setup_logger
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price_requirements
)

logger = setup_logger(__name__)

class OrderManager:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Validates inputs and places an order via the Binance Client."""
        # 1. Validation
        try:
            symbol = validate_symbol(symbol)
            side = validate_side(side)
            order_type = validate_order_type(order_type)
            quantity = validate_quantity(quantity)
            validate_price_requirements(order_type, price, stop_price)
        except ValueError as e:
            logger.error(f"Validation Failure: {str(e)}")
            raise e
            
        # 2. Preparation Summary
        req_summary = (
            f"Pre-flight Check [{order_type}]: "
            f"Symbol={symbol}, Side={side}, Qty={quantity}, "
            f"Price={price}, StopPrice={stop_price}"
        )
        logger.info(req_summary)
        
        # 3. Execution
        try:
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stopPrice=stop_price
            )
            
            # Format normalized response to return to CLI
            return {
                "success": True,
                "orderId": response.get("orderId"),
                "status": response.get("status"),
                "executedQty": response.get("executedQty", 0.0),
                "avgPrice": response.get("avgPrice", 0.0),
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
