"""Request models para los endpoints."""
from typing import Optional
from pydantic import BaseModel, Field

from .market import (
    BinanceMarketState,
    PositionState,
    TradingViewSignalData,
    BinanceContext,
)


# ==============================================================================
# SIGNAL CONFIRMATION (COMPRA)
# ==============================================================================

class SignalConfirmationRequest(BaseModel):
    """
    Request para confirmar/desconfirmar una señal de TradingView.

    Laya recibe la alerta de TradingView + contexto de Binance
    y decide si CONFIRMA o RECHAZA la señal de compra.
    """
    tradingview_data: TradingViewSignalData
    binance_context: BinanceContext
    custom_rules: Optional[str] = Field(
        None,
        example="Solo comprar si RSI < 70 y volumen delta > 0"
    )


# ==============================================================================
# BUY EVALUATION (para backward compatibility o uso simple)
# ==============================================================================

class BuyEvaluationRequest(BaseModel):
    """Request simple para evaluar si comprar o no un activo."""
    market_data: BinanceMarketState
    custom_rules: Optional[str] = Field(
        None,
        example="Estrategia spot de bajo riesgo, no comprar si la caída en 24h es mayor al 10%"
    )


# ==============================================================================
# EXIT/EVAL CHECK (VENTA - monitoreo de posición)
# ==============================================================================

class ExitCheckRequest(BaseModel):
    """
    Request para evaluar si SALIR de una posición abierta.

    Este request llega cada 40 segundos cuando hay una posición abierta.
    Laya decide si mantenerse en la posición o salir.
    """
    action: str = Field(..., example="CHECK_SELL")
    symbol: str = Field(..., example="SOLUSDT")
    entry_price: float = Field(..., example=104.28)
    current_price: float = Field(..., example=104.36)
    binance_context: BinanceContext
    custom_rules: Optional[str] = Field(
        None,
        example="Tomar ganancias si PnL > 2% o cortar pérdidas si PnL < -1%"
    )


# ==============================================================================
# EXIT EVALUATION (para uso genérico con PositionState)
# ==============================================================================

class ExitEvaluationRequest(BaseModel):
    """Request genérico para evaluar si salir o no de una posición."""
    market_data: BinanceMarketState
    position_data: PositionState
    custom_rules: Optional[str] = Field(
        None,
        example="Tomar ganancias si PnL > 5% o cortar pérdidas si PnL < -3%"
    )
