"""Endpoint para evaluar salida de posición (CHECK_SELL)."""
from fastapi import APIRouter, Depends, HTTPException

from models import ExitCheckRequest, ExitCheckResponse
from services import predict_exit_check
from api.deps import verify_api_key

router = APIRouter()


@router.post("/v1/check-sell", response_model=ExitCheckResponse)
async def check_sell(req: ExitCheckRequest):
    """
    Evalúa si se debe SALIR de una posición abierta (monitoreo cada 40 segundos).

    Laya recibe:
    - Symbol, entry_price, current_price
    - Binance context actualizado (order flow, derivados, order book, BTC)

    Returns:
        - should_exit: Booleano indicando si salir o no
        - should_exit_score: Score de confianza (0-1)
        - entry_price, current_price, pnl_percent
        - trace: Trace completo con preguntas, respuestas y state
    """
    try:
        result = predict_exit_check(
            symbol=req.symbol,
            entry_price=req.entry_price,
            current_price=req.current_price,
            binance_context=req.binance_context,
            custom_rules=req.custom_rules,
        )
        return ExitCheckResponse(
            symbol=req.symbol,
            success=True,
            decision_type="exit_check",
            should_exit=result["should_exit"],
            should_exit_score=result["should_exit_score"],
            entry_price=result["entry_price"],
            current_price=result["current_price"],
            pnl_percent=result["pnl_percent"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
