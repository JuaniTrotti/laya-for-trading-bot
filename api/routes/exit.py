"""Endpoint para evaluar salida de posición (VENTA)."""
from fastapi import APIRouter, HTTPException

from models import SellRequest, SellResponse
from services import predict_sell
from api.deps import verify_api_key

router = APIRouter()


@router.post("/v1/check-sell", response_model=SellResponse)
async def check_sell(req: SellRequest):
    """
    Evalúa si se debe SALIR de una posición (monitoreo cada 40 segundos).

    Una sola pregunta a Laya: ¿Debo vender?
    """
    try:
        result = predict_sell(
            symbol=req.symbol,
            entry_price=req.entry_price,
            current_price=req.current_price,
            binance_context=req.binance_context,
            custom_rules=req.custom_rules,
        )
        return SellResponse(
            symbol=result["symbol"],
            decision=result["decision"],
            score=result["score"],
            entry_price=result["entry_price"],
            current_price=result["current_price"],
            pnl_percent=result["pnl_percent"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
