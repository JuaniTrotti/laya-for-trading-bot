"""Endpoint para confirmar señales de TradingView (COMPRAR)."""
from fastapi import APIRouter, HTTPException

from models import BuyRequest, BuyResponse
from services import predict_buy
from api.deps import verify_api_key

router = APIRouter()


@router.post("/v1/confirm-signal", response_model=BuyResponse)
async def confirm_signal(req: BuyRequest):
    """
    Confirma o Rechaza una señal de TradingView para COMPRAR.

    Una sola pregunta a Laya: ¿Debo comprar?
    """
    try:
        result = predict_buy(
            tradingview_data=req.tradingview_data,
            binance_context=req.binance_context,
            custom_rules=req.custom_rules,
        )
        return BuyResponse(
            symbol=result["symbol"],
            decision=result["decision"],
            score=result["score"],
            signal_event=result["signal_event"],
            signal_price=result["signal_price"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
