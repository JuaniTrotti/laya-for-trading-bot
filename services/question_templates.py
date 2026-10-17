"""Templates de preguntas para Laya."""
from typing import Dict, Any


def build_signal_confirmation_questions(strategy_rules: str) -> Dict[str, Any]:
    """
    Construye las preguntas para CONFIRMAR o RECHAZAR una señal de TradingView.

    Laya recibe:
    - Datos de la señal (precio, stop loss, take profit, scores, metrics)
    - Contexto de Binance (order flow, derivados, order book, BTC)

    Returns:
        Dict con preguntas para decidir si confirmar la señal de compra.
    """
    return {
        "confirm_signal": {
            "type": "noul",
            "instructions": (
                "A TradingView alert triggered a BUY_SIGNAL. "
                "Analyze ALL available data (TradingView scores/metrics, Binance order flow, "
                "derivatives, BTC context) and decide: Should we CONFIRM and EXECUTE this trade "
                "or REJECT it? "
                f"Consider these rules: {strategy_rules}"
            ),
        },
        "signal_quality": {
            "type": "choice",
            "instructions": "Based on the TradingView signal scores (structure, volume, rsi, trend), how strong is this signal?",
            "criteria": {
                "strong": "High scores in multiple categories, especially structure and RSI",
                "moderate": "Decent scores but some weak areas",
                "weak": "Low total score or weak in critical categories like structure"
            }
        },
        "order_flow_alignment": {
            "type": "choice",
            "instructions": "How does the Binance order flow align with the BUY signal?",
            "criteria": {
                "aligned": "Volume delta positive or buyer dominance, suggesting buying pressure",
                "neutral": "Mixed signals in order flow",
                "diverging": "Heavy seller pressure, volume delta negative despite buy signal"
            }
        },
        "risk_assessment": {
            "type": "choice",
            "instructions": "What is your risk assessment considering the entry price, stop loss, and current market conditions?",
            "criteria": {
                "low_risk": "Tight stop loss, good R/R ratio (>2), favorable BTC context",
                "medium_risk": "Acceptable stop loss and R/R ratio",
                "high_risk": "Wide stop loss, poor R/R ratio, or adverse BTC context (BTC dumping)"
            }
        },
        "action_recommended": {
            "type": "choice",
            "instructions": "What action should the trading bot take?",
            "criteria": {
                "execute_buy": "Signal is confirmed - high confidence, execute the trade",
                "wait_and_watch": "Signal looks ok but not great - wait for better entry or more confirmation",
                "reject_signal": "Signal is weak or contradicted by Binance data - do not trade"
            }
        }
    }


def build_buy_questions(strategy_rules: str) -> Dict[str, Any]:
    """
    Construye las preguntas para evaluar entrada en posición (COMPRAR).

    Returns:
        Dict con preguntas tipo noul y choice para decisión de compra.
    """
    return {
        "should_buy": {
            "type": "noul",
            "instructions": (
                "Based on the current market data and strategy rules, "
                f"should we open a LONG position? Strategy context: {strategy_rules}"
            ),
        },
        "risk_level": {
            "type": "choice",
            "instructions": "What is the risk level of entering this position right now?",
            "criteria": {
                "low": "Strong support, healthy volume, non-extreme change, favorable RSI",
                "medium": "Moderate volatility or neutral technical indicators",
                "high": "Extreme dump, low volume, severe downside risk, overbought RSI",
            },
        },
        "entry_quality": {
            "type": "choice",
            "instructions": "How would you rate the current entry quality?",
            "criteria": {
                "excellent": "Perfect setup with clear catalyst, strong support, and confirmation",
                "good": "Acceptable entry with decent risk/reward ratio",
                "poor": "Risky entry without clear confirmation or support nearby",
            },
        },
        "action_recommended": {
            "type": "choice",
            "instructions": "Which action should the trading bot take regarding entry?",
            "criteria": {
                "buy_now": "Clear entry signal with acceptable risk - execute now",
                "wait_for_dip": "Bullish context but price needs better entry point - patient",
                "avoid": "High risk, declining trend, or unfavorable setup - skip",
            },
        },
    }


def build_exit_questions(strategy_rules: str) -> Dict[str, Any]:
    """
    Construye las preguntas para evaluar salida de posición (VENDER/SALIR).

    Returns:
        Dict con preguntas tipo noul y choice para decisión de salida.
    """
    return {
        "should_exit": {
            "type": "noul",
            "instructions": (
                "Based on the current market data, position state, and strategy rules, "
                f"should we close this position now? Strategy context: {strategy_rules}"
            ),
        },
        "exit_urgency": {
            "type": "choice",
            "instructions": "How urgent is it to exit this position?",
            "criteria": {
                "immediate": "Critical: Stop loss hit, massive dump incoming, or take profit target reached",
                "consider": "Moderate concern: Watch for further deterioration, prepare to exit",
                "hold": "No urgency: Position is safe, consider holding for more gains",
            },
        },
        "exit_reason": {
            "type": "choice",
            "instructions": "If exiting, what is the primary reason?",
            "criteria": {
                "take_profit": "Profit target reached, secure gains",
                "stop_loss": "Loss limit reached, cut losses",
                "risk_management": "Overall portfolio risk, rebalancing, or market conditions changed",
                "signal_reversal": "Technical indicators show clear reversal pattern",
            },
        },
        "action_recommended": {
            "type": "choice",
            "instructions": "Which action should the trading bot take regarding this position?",
            "criteria": {
                "exit_now": "Close position immediately - urgent exit recommended",
                "set_stop_loss": "Don't exit yet but tighten stop loss to protect profits",
                "hold": "Maintain position, conditions are still favorable",
            },
        },
    }
