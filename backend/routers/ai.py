from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import AIChatRequest, AIChatResponse
from backend.ai.groq_provider import GroqProvider
from backend.trading.paper_trader import PaperTrader
from backend.data.twelve_data import TwelveDataClient
from backend.trading.strategy import generate_signal

router = APIRouter(prefix="/api/ai", tags=["AI"])

def get_ai_provider():
    return GroqProvider()

def get_market_client():
    return TwelveDataClient()

@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    request: AIChatRequest,
    provider: GroqProvider = Depends(get_ai_provider),
    db: Session = Depends(get_db),
    market_client: TwelveDataClient = Depends(get_market_client)
):
    try:
        context_parts = []
        
        # Add Portfolio Context
        trader = PaperTrader(db, market_client)
        snapshot = trader.get_portfolio_snapshot()
        context_parts.append(f"PORTFOLIO: Cash=${snapshot.cash:.2f}, Total Value=${snapshot.portfolio_value:.2f}, Realized P&L=${snapshot.realized_pnl:.2f}")
        
        # Add Symbol Context if provided
        if request.symbol:
            try:
                history = await market_client.get_history(request.symbol)
                signal_res = generate_signal(request.symbol, history)
                context_parts.append(f"SYMBOL {request.symbol}: Signal is {signal_res.signal} at price ${signal_res.price:.2f}.")
                context_parts.append(f"INDICATORS for {request.symbol}: EMA20={signal_res.indicators.ema20}, EMA50={signal_res.indicators.ema50}, RSI={signal_res.indicators.rsi}, MACD={signal_res.indicators.macd}.")
                context_parts.append(f"STRATEGY REASONING for {request.symbol}: {' '.join(signal_res.reasons)}")
            except Exception as e:
                context_parts.append(f"Could not fetch signal for {request.symbol} (Error: {str(e)}).")

        context = "\n".join(context_parts)
        
        reply = provider.generate_chat_response(context, request.message)
        return AIChatResponse(reply=reply)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
