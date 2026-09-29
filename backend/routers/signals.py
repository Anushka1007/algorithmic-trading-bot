from fastapi import APIRouter, Depends, Query, HTTPException
from backend.data.twelve_data import TwelveDataClient
from backend.schemas import SignalResponse
from backend.trading.strategy import generate_signal

router = APIRouter(prefix="/api/signals", tags=["Signals"])

def get_market_client():
    return TwelveDataClient()

@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal(
    symbol: str, 
    client: TwelveDataClient = Depends(get_market_client)
):
    try:
        # Request enough data to calculate EMA50 + buffer
        history = await client.get_history(symbol, interval="1day", outputsize=100)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")

    signal = generate_signal(symbol, history)
    return signal
