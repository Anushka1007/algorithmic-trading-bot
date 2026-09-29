import httpx
from datetime import datetime, timedelta
import time
from backend.config import settings
from backend.schemas import Quote, OHLCV, HistoricalData
from fastapi import HTTPException

BASE_URL = "https://api.twelvedata.com"

# Simple in-memory cache: (symbol, interval, outputsize) -> (timestamp, HistoricalData)
_history_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache

class TwelveDataClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.twelve_data_api_key

    async def get_quote(self, symbol: str) -> Quote:
        if not self.api_key or self.api_key.startswith("dummy") or self.api_key == "your_twelve_data_key_here":
            raise HTTPException(status_code=500, detail="Twelve Data API key is missing or dummy.")
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{BASE_URL}/quote",
                    params={"symbol": symbol, "apikey": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                
                if "status" in data and data["status"] == "error":
                    raise HTTPException(status_code=400, detail=data.get("message", "Twelve Data API error"))
                    
                if not data:
                    raise HTTPException(status_code=404, detail="Symbol not found or empty response")

                return Quote(
                    symbol=data.get("symbol", symbol),
                    price=float(data["close"]),
                    timestamp=int(data.get("timestamp", time.time())),
                    is_live=data.get("is_market_open", False),
                    source="Twelve Data"
                )
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=502, detail="Malformed provider response")

    async def get_history(self, symbol: str, interval: str = "1day", outputsize: int = 100) -> HistoricalData:
        cache_key = (symbol, interval, outputsize)
        if cache_key in _history_cache:
            cache_time, cached_data = _history_cache[cache_key]
            if time.time() - cache_time < CACHE_TTL_SECONDS:
                cached_data.is_cached = True
                return cached_data

        if not self.api_key or self.api_key.startswith("dummy") or self.api_key == "your_twelve_data_key_here":
            raise HTTPException(status_code=500, detail="Twelve Data API key is missing or dummy.")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{BASE_URL}/time_series",
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "outputsize": outputsize,
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if "status" in data and data["status"] == "error":
                    raise HTTPException(status_code=400, detail=data.get("message", "Twelve Data API error"))
                    
                values = data.get("values", [])
                if not values:
                    raise HTTPException(status_code=404, detail="No historical data found for symbol")

                ohlcv_list = [
                    OHLCV(
                        datetime=v["datetime"],
                        open=float(v["open"]),
                        high=float(v["high"]),
                        low=float(v["low"]),
                        close=float(v["close"]),
                        volume=int(v.get("volume", 0))
                    ) for v in values
                ]

                historical_data = HistoricalData(
                    symbol=symbol,
                    interval=interval,
                    data=ohlcv_list,
                    is_cached=False
                )
                
                # Update cache
                _history_cache[cache_key] = (time.time(), historical_data)
                
                return historical_data
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=502, detail="Malformed provider response")
