"""Response models para los endpoints."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class EvaluationInput(BaseModel):
    """Datos de entrada que se enviaron a Laya."""
    symbol: str
    market_data: Dict[str, Any]
    laya_state: Dict[str, str]


class QuestionItem(BaseModel):
    """Pregunta enviada a Laya."""
    key: str
    type: str
    instructions: str


class AnswerItem(BaseModel):
    """Respuesta de Laya."""
    question_key: str
    answer_value: Any
    score: Optional[float] = None
    reasoning: Optional[str] = None


class EvaluationResult(BaseModel):
    """
    Trace completo de la evaluación para debugging/UI.
    """
    input_data: EvaluationInput
    questions: List[QuestionItem]
    answers: List[AnswerItem]
    routing: Optional[Dict[str, Any]] = None


class BuyResponse(BaseModel):
    """
    Response para decisión de COMPRA.
    """
    symbol: str
    decision: bool              # True = comprar, False = rechazar
    score: Optional[float]     # Confianza 0-1
    signal_event: str
    signal_price: float
    trace: EvaluationResult


class SellResponse(BaseModel):
    """
    Response para decisión de VENTA.
    """
    symbol: str
    decision: bool              # True = vender, False = mantener
    score: Optional[float]     # Confianza 0-1
    entry_price: float
    current_price: float
    pnl_percent: float
    trace: EvaluationResult
