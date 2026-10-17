"""Endpoint para confirmar/rechazar señales de TradingView."""
from fastapi import APIRouter, Depends, HTTPException

from models import SignalConfirmationRequest, SignalConfirmationResponse
from services import predict_signal_confirmation
from api.deps import verify_api_key

router = APIRouter()


@router.post("/v1/confirm-signal", response_model=SignalConfirmationResponse)
async def confirm_signal(req: SignalConfirmationRequest):
    """
    Confirma o Rechaza una señal de TradingView.

    Laya recibe:
    - TradingView signal data (precio, stop loss, take profit, scores, metrics)
    - Binance context (order flow, derivados, order book, BTC)
    - Custom rules opcionales

    Returns:
        - signal_confirmed: Booleano indicando si confirmar la señal
        - confirm_score: Score de confianza (0-1)
        - trace: Trace completo con preguntas, respuestas y state
    """
    try:
        result = predict_signal_confirmation(
            tradingview_data=req.tradingview_data,
            binance_context=req.binance_context,
            custom_rules=req.custom_rules,
        )
        return SignalConfirmationResponse(
            symbol=req.tradingview_data.ticker,
            success=True,
            decision_type="signal_confirmation",
            signal_confirmed=result["signal_confirmed"],
            confirm_score=result["confirm_score"],
            signal_event=result["signal_event"],
            signal_price=result["signal_price"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
