"""Endpoint para evaluar compra."""
from fastapi import APIRouter, Depends, HTTPException

from models import BuyEvaluationRequest, BuyEvaluationResponse
from services import predict_buy
from api.deps import verify_api_key

router = APIRouter()


@router.post("/v1/evaluate-buy", response_model=BuyEvaluationResponse)
async def evaluate_buy(req: BuyEvaluationRequest):
    """
    Evalúa si un activo es elegible para COMPRAR/entrar en posición.

    Incluye trace completo para debugging y visualización en UI:
    - input_data: datos de mercado y reglas enviadas
    - questions: preguntas que se hicieron a Laya
    - answers: respuestas de Laya con scores
    - routing: info de routing de Laya
    """
    try:
        result = predict_buy(req.market_data, req.custom_rules)
        return BuyEvaluationResponse(
            symbol=req.market_data.symbol,
            success=True,
            decision_type="buy_entry",
            should_buy=result["should_buy"],
            should_buy_score=result["should_buy_score"],
            trace=result["trace"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
