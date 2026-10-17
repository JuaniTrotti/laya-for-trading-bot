"""Modelos de datos de mercado y posición."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ==============================================================================
# TRADINGVIEW SIGNAL DATA
# ==============================================================================

class TradingViewScores(BaseModel):
    """Scores individuales de TradingView."""
    structure: int = Field(..., example=25)
    volume: int = Field(..., example=0)
    rsi: int = Field(..., example=25)
    trend: int = Field(..., example=10)


class TradingViewMetrics(BaseModel):
    """Métricas técnicas de TradingView."""
    vol_ratio: float = Field(..., example=0.46)
    rsi: float = Field(..., example=67.45)
    atr: float = Field(..., example=0.14)
    bb_width: float = Field(..., example=0.0063)
    is_squeezed: bool = Field(..., example=True)


class TradingViewSignalData(BaseModel):
    """Datos de la señal recibida desde TradingView."""
    event: str = Field(..., example="BUY_SIGNAL")
    ticker: str = Field(..., example="SOLUSDT")
    price: float = Field(..., example=104.28)
    stop_loss: Optional[float] = Field(None, example=104.07)
    take_profit: Optional[float] = Field(None, example=104.70)
    score_total: int = Field(..., example=60)
    scores: TradingViewScores
    metrics: TradingViewMetrics


# ==============================================================================
# BINANCE CONTEXT
# ==============================================================================

class SymbolPriceData(BaseModel):
    """Precio actual del símbolo."""
    symbol: str = Field(..., example="SOLUSDT")
    current_price: float = Field(..., example=104.36)


class OrderFlowData(BaseModel):
    """Order flow data de Binance."""
    buyer_taker_volume: float = Field(..., example=2927.3)
    seller_taker_volume: float = Field(..., example=6781.74)
    volume_delta: float = Field(..., example=-3854.44)
    buyer_dominance: bool = Field(..., example=False)


class DerivativesData(BaseModel):
    """Datos de derivados de Binance."""
    open_interest: float = Field(..., example=8938804.37)
    top_long_short_ratio: float = Field(..., example=2.3359)
    funding_rate: float = Field(..., example=0.00001031)


class OrderBookData(BaseModel):
    """Datos del order book de Binance."""
    ask_liquidity_next_1pct: float = Field(..., example=213056.24)
    best_bid: float = Field(..., example=104.36)
    best_ask: float = Field(..., example=104.37)
    spread: float = Field(..., example=0.01)


class BTCContextData(BaseModel):
    """Contexto de BTC para correlación."""
    btc_price: float = Field(..., example=81704)
    btc_5m_change_pct: float = Field(..., example=-0.047)
    btc_is_stable_or_bullish: bool = Field(..., example=True)


class BinanceContext(BaseModel):
    """
    Contexto completo de Binance.
    Se usa tanto para señales de compra como para monitoreo de venta.
    """
    # Opcional: viene en CHECK_SELL
    symbol_price: Optional[SymbolPriceData] = None
    # Siempre presentes
    order_flow: OrderFlowData
    derivatives: DerivativesData
    order_book: OrderBookData
    btc_context: BTCContextData


# ==============================================================================
# POSITION STATE (para decisiones de exit)
# ==============================================================================

class PositionState(BaseModel):
    """Estado de una posición abierta."""
    entry_price: float = Field(..., example=64200.00)
    current_price: float = Field(..., example=65400.50)
    pnl_percent: float = Field(..., example=1.87)
    holding_time: Optional[str] = Field(None, example="4h 30m")
    stop_loss_price: Optional[float] = Field(None, example=62000.00)


# ==============================================================================
# GENERIC MARKET STATE (mantener para compatibilidad)
# ==============================================================================

class BinanceMarketState(BaseModel):
    """Estado de mercado genérico con datos de Binance."""
    symbol: str = Field(..., example="BTCUSDT")
    price: float = Field(..., example=65400.50)
    change_24h_percent: float = Field(..., example=-3.45)
    volume_24h_usdt: float = Field(..., example=450000000.0)
    rsi_14: Optional[float] = Field(None, example=28.5)
    trend_description: Optional[str] = Field(
        None,
        example="Soporte clave alcanzado con divergencia alcista en RSI"
    )
