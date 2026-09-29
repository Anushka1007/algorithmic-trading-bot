from fastapi import APIRouter, Depends, Query
from backend.data.twelve_data import TwelveDataClient
from backend.schemas import Quote, HistoricalData

router = APIRouter(prefix="/api/market", tags=["Market Data"])

def get_market_client():
    return TwelveDataClient()

@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(symbol: str, client: TwelveDataClient = Depends(get_market_client)):
    return await client.get_quote(symbol)

@router.get("/history/{symbol}", response_model=HistoricalData)
async def get_history(
    symbol: str, 
    interval: str = Query("1day", description="Interval (e.g. 1min, 5min, 1day)"), 
    outputsize: int = Query(100, ge=1, le=5000),
    client: TwelveDataClient = Depends(get_market_client)
):
    return await client.get_history(symbol, interval, outputsize)
