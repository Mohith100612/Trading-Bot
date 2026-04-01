import time
import hmac
import hashlib
import httpx
from urllib.parse import urlencode
from typing import Dict, Any, Optional

from bot.logger import setup_logger

logger = setup_logger(__name__)

class BinanceFuturesClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API Key and Secret must not be empty.")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = httpx.Client(
            headers={
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=10.0
        )

    def _generate_signature(self, query_string: str) -> str:
        """Generates HMAC SHA256 signature required by Binance API."""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method to handle signed requests and error logging.
        Binance Futures expects parameters in the query string even for POST requests.
        """
        if params is None:
            params = {}
            
        # Add timestamp (required by signed endpoints)
        params['timestamp'] = int(time.time() * 1000)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        query_string += f"&signature={signature}"
        
        url = f"{self.BASE_URL}{endpoint}?{query_string}"
        
        # Clean URL logged locally (we avoid logging raw secret directly)
        log_url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.info(f"API Request | {method} {log_url} | Params: {params}")
            
            if method == "GET":
                response = self.client.get(url)
            elif method == "POST":
                response = self.client.post(url)
            elif method == "DELETE":
                response = self.client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"API Response | Status: {response.status_code} | Body: {response_json}")
            return response_json
            
        except httpx.HTTPStatusError as e:
            err_text = e.response.text
            status = e.response.status_code
            logger.error(f"HTTP Return | Status: {status} | Error: {err_text}")
            raise Exception(f"API Error ({status}): {err_text}")
        except httpx.RequestError as e:
            logger.error(f"Network Failure | {str(e)}")
            raise Exception(f"Network Error: Unable to reach Binance Futures testnet. Details: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Error | {str(e)}")
            raise e

    def get_exchange_info(self) -> Dict[str, Any]:
        """Gets exchange information (public endpoint)."""
        url = f"{self.BASE_URL}/fapi/v1/exchangeInfo"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, 
                    price: Optional[float] = None, stopPrice: Optional[float] = None) -> Dict[str, Any]:
        """
        Places an order.
        Valid types: MARKET, LIMIT, STOP_MARKET, etc.
        """
        endpoint = "/fapi/v1/order"
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }
        
        if order_type.upper() == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
            
        if order_type.upper() == "STOP_MARKET":
            params["stopPrice"] = stopPrice
            # Binance testing env can sometimes require 'closePosition' or other flags
            # for basic stop market, stopPrice is required
            
        return self._request("POST", endpoint, params)
