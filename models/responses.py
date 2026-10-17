"""Response models para los endpoints."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class EvaluationInput(BaseModel):
    """Datos de entrada que se enviaron a Laya para procesar."""
    symbol: str
    market_data: Dict[str, Any]
    position_data: Optional[Dict[str, Any]] = None
    custom_rules: Optional[str] = None
    # State final que se construyó para Laya
    laya_state: Dict[str, str]


class QuestionItem(BaseModel):
    """Una pregunta individual con su configuración."""
    key: str
    type: str  # "noul" o "choice"
    instructions: str
    criteria: Optional[Dict[str, str]] = None


class AnswerItem(BaseModel):
    """Respuesta individual de Laya."""
    question_key: str
    answer_value: Any
    score: Optional[float] = None
    reasoning: Optional[str] = None


class EvaluationResult(BaseModel):
    """
    Resultado completo de una evaluación de Laya.
    Incluye todo lo necesario para visualizar el proceso de decisión en una UI.
    """
    # Inputs
    input_data: EvaluationInput
    # Preguntas que se enviaron
    questions: List[QuestionItem]
    # Respuestas de Laya
    answers: List[AnswerItem]
    # Info de routing
    routing: Optional[Dict[str, Any]] = None
    # Decisión final
    decision: Dict[str, Any]


# ==============================================================================
# SIGNAL CONFIRMATION RESPONSE (COMPRA)
# ==============================================================================

class SignalConfirmationResponse(BaseModel):
    """
    Response para confirmación de señal de TradingView.
    Incluye trace completo para debugging/UI.
    """
    symbol: str
    success: bool
    decision_type: str = "signal_confirmation"
    # Decisión principal
    signal_confirmed: bool
    confirm_score: Optional[float] = None
    signal_event: str
    signal_price: float
    # Trace completo
    trace: EvaluationResult


# ==============================================================================
# BUY EVALUATION RESPONSE
# ==============================================================================

class BuyEvaluationResponse(BaseModel):
    """
    Response para evaluación de compra simple.
    Incluye trace completo para debugging/UI.
    """
    symbol: str
    success: bool
    decision_type: str = "buy_entry"
    # Decisión principal
    should_buy: bool
    should_buy_score: Optional[float] = None
    # Trace completo
    trace: EvaluationResult


# ==============================================================================
# EXIT CHECK RESPONSE (VENTA - monitoreo de posición)
# ==============================================================================

class ExitCheckResponse(BaseModel):
    """
    Response para check de salida (monitoreo de posición cada 40 segundos).
    Incluye trace completo para debugging/UI.
    """
    symbol: str
    success: bool
    decision_type: str = "exit_check"
    # Decisión principal
    should_exit: bool
    should_exit_score: Optional[float] = None
    # Info de la posición
    entry_price: float
    current_price: float
    pnl_percent: float
    # Trace completo
    trace: EvaluationResult


# ==============================================================================
# EXIT EVALUATION RESPONSE
# ==============================================================================

class ExitEvaluationResponse(BaseModel):
    """
    Response para evaluación de salida genérica.
    Incluye trace completo para debugging/UI.
    """
    symbol: str
    success: bool
    decision_type: str = "exit_position"
    # Decisión principal
    should_exit: bool
    should_exit_score: Optional[float] = None
    # Trace completo
    trace: EvaluationResult
