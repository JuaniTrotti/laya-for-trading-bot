"""Request models para los endpoints."""
from typing import Optional
from pydantic import BaseModel, Field

from .market import TradingViewSignalData, BinanceContext


class BuyRequest(BaseModel):
    """
    Request para confirmar una señal de TradingView (COMPRAR).
    """
    tradingview_data: TradingViewSignalData
    binance_context: BinanceContext
    custom_rules: Optional[str] = Field(
        None,
        example="Solo comprar si RSI < 70 y volumen delta > 0"
    )


class SellRequest(BaseModel):
    """
    Request para evaluar si SALIR de una posición (VENTA).
    Monitoreo cada 40 segundos mientras hay posición abierta.
    """
    symbol: str = Field(..., example="SOLUSDT")
    entry_price: float = Field(..., example=104.28)
    current_price: float = Field(..., example=104.36)
    binance_context: BinanceContext
    custom_rules: Optional[str] = Field(
        None,
        example="Tomar ganancias si PnL > 2%"
    )
