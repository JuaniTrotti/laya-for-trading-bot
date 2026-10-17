"""Servicio de Laya para inferencia."""
from typing import Dict, Any, Optional, List

from laya import Router

from config import MODEL_PRELOAD
from models.market import TradingViewSignalData, BinanceContext
from models.responses import EvaluationInput, EvaluationResult, QuestionItem, AnswerItem
from .question_templates import build_signal_confirmation_questions, build_exit_questions


# Singleton del router Laya
_router: Optional[Router] = None


def get_router() -> Router:
    """Obtiene o crea el router de Laya (singleton)."""
    global _router
    if _router is None:
        _router = Router(preload=MODEL_PRELOAD)
    return _router


# ==============================================================================
# STATE BUILDERS
# ==============================================================================

def build_laya_state_from_signal(
    tradingview_data: TradingViewSignalData,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, str]:
    """
    Construye el state para Laya con datos de TradingView + Binance (COMPRA).
    """
    tv = tradingview_data
    bc = binance_context

    return {
        # TradingView Signal
        "signal_type": tv.event,
        "signal_ticker": tv.ticker,
        "signal_price": f"${tv.price}",
        "signal_score_total": str(tv.score_total),
        "signal_score_structure": str(tv.scores.structure),
        "signal_score_volume": str(tv.scores.volume),
        "signal_score_rsi": str(tv.scores.rsi),
        "signal_score_trend": str(tv.scores.trend),
        # TradingView Metrics
        "signal_vol_ratio": str(tv.metrics.vol_ratio),
        "signal_rsi": str(tv.metrics.rsi),
        "signal_atr": str(tv.metrics.atr),
        "signal_bb_width": str(tv.metrics.bb_width),
        "signal_is_squeezed": "YES" if tv.metrics.is_squeezed else "NO",
        # Binance Context
        "binance_order_flow": f"Volume Delta: {bc.order_flow.volume_delta:,.2f} ({'Buyer' if bc.order_flow.buyer_dominance else 'Seller'} dominant)",
        "binance_derivatives": f"OI: ${bc.derivatives.open_interest:,.2f}, L/S: {bc.derivatives.top_long_short_ratio:.2f}, Funding: {bc.derivatives.funding_rate:.6f}",
        "binance_order_book_spread": f"${bc.order_book.spread}",
        "binance_btc_context": f"BTC: ${bc.btc_context.btc_price:,}, 5m: {bc.btc_context.btc_5m_change_pct:.3f}%, {'Bullish' if bc.btc_context.btc_is_stable_or_bullish else 'Bearish'}",
        # Strategy
        "strategy_rules": custom_rules or "Estrategia general de trading",
    }


def build_laya_state_from_exit_check(
    symbol: str,
    entry_price: float,
    current_price: float,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, str]:
    """
    Construye el state para Laya con datos de posición + Binance (VENTA).
    """
    bc = binance_context
    pnl_percent = ((current_price - entry_price) / entry_price) * 100

    return {
        # Position
        "position_symbol": symbol,
        "position_entry_price": f"${entry_price}",
        "position_current_price": f"${current_price}",
        "position_pnl_percent": f"{pnl_percent:.2f}%",
        # Binance Context
        "binance_order_flow": f"Volume Delta: {bc.order_flow.volume_delta:,.2f} ({'Buyer' if bc.order_flow.buyer_dominance else 'Seller'} dominant)",
        "binance_derivatives": f"OI: ${bc.derivatives.open_interest:,.2f}, L/S: {bc.derivatives.top_long_short_ratio:.2f}, Funding: {bc.derivatives.funding_rate:.6f}",
        "binance_order_book": f"Bid: ${bc.order_book.best_bid}, Ask: ${bc.order_book.best_ask}, Spread: ${bc.order_book.spread}",
        "binance_btc_context": f"BTC: ${bc.btc_context.btc_price:,}, 5m: {bc.btc_context.btc_5m_change_pct:.3f}%, {'Bullish' if bc.btc_context.btc_is_stable_or_bullish else 'Bearish'}",
        # Strategy
        "strategy_rules": custom_rules or "Estrategia general de trading",
    }


# ==============================================================================
# HELPERS
# ==============================================================================

def _build_evaluation_result(
    symbol: str,
    market_data: Dict[str, Any],
    laya_state: Dict[str, str],
    questions: Dict[str, Any],
    laya_raw_result: Dict[str, Any],
) -> EvaluationResult:
    """Construye el EvaluationResult con todo el trace."""
    answers = laya_raw_result.get("answers", {})
    scores = laya_raw_result.get("scores") or laya_raw_result.get("routing", {}).get("scores")

    question_items = [
        QuestionItem(
            key=key,
            type=config.get("type", "noul"),
            instructions=config.get("instructions", ""),
        )
        for key, config in questions.items()
    ]

    answer_items = []
    for key, config in questions.items():
        raw_answer = answers.get(key)
        answer_value = raw_answer
        score = scores.get(key) if scores else None
        reasoning = None

        if isinstance(raw_answer, dict):
            answer_value = raw_answer.get("value", raw_answer)
            score = raw_answer.get("score") or score
            reasoning = raw_answer.get("reasoning")

        answer_items.append(AnswerItem(
            question_key=key,
            answer_value=answer_value,
            score=score,
            reasoning=reasoning,
        ))

    return EvaluationResult(
        input_data=EvaluationInput(
            symbol=symbol,
            market_data=market_data,
            laya_state=laya_state,
        ),
        questions=question_items,
        answers=answer_items,
        routing=laya_raw_result.get("routing"),
    )


# ==============================================================================
# PREDICT FUNCTIONS
# ==============================================================================

def predict_buy(
    tradingview_data: TradingViewSignalData,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, Any]:
    """
    Ejecuta decisión de COMPRA usando Laya.
    Una pregunta: should_buy = True (comprar) o False (rechazar).
    """
    router = get_router()
    laya_state = build_laya_state_from_signal(tradingview_data, binance_context, custom_rules)
    questions = build_signal_confirmation_questions(
        strategy_rules=custom_rules or "Estrategia general de trading",
        ticker=tradingview_data.ticker,
        price=tradingview_data.price,
    )
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    # Extraer decisión
    should_buy_raw = answers.get("should_buy", False)
    if isinstance(should_buy_raw, dict):
        decision = bool(should_buy_raw.get("value", should_buy_raw))
        score = should_buy_raw.get("score") or scores.get("should_buy") if scores else None
    else:
        decision = bool(should_buy_raw)
        score = scores.get("should_buy") if scores else None

    trace = _build_evaluation_result(
        symbol=tradingview_data.ticker,
        market_data=tradingview_data.model_dump(),
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "symbol": tradingview_data.ticker,
        "decision": decision,
        "score": score,
        "signal_event": tradingview_data.event,
        "signal_price": tradingview_data.price,
        "trace": trace,
    }


def predict_sell(
    symbol: str,
    entry_price: float,
    current_price: float,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, Any]:
    """
    Ejecuta decisión de VENTA usando Laya.
    Una pregunta: should_sell = True (vender) o False (mantener).
    """
    router = get_router()
    laya_state = build_laya_state_from_exit_check(
        symbol=symbol,
        entry_price=entry_price,
        current_price=current_price,
        binance_context=binance_context,
        custom_rules=custom_rules,
    )
    pnl_percent = ((current_price - entry_price) / entry_price) * 100
    questions = build_exit_questions(
        strategy_rules=custom_rules or "Estrategia general de trading",
        symbol=symbol,
        entry_price=entry_price,
        current_price=current_price,
        pnl_percent=pnl_percent,
    )
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    # Extraer decisión
    should_sell_raw = answers.get("should_sell", False)
    if isinstance(should_sell_raw, dict):
        decision = bool(should_sell_raw.get("value", should_sell_raw))
        score = should_sell_raw.get("score") or scores.get("should_sell") if scores else None
    else:
        decision = bool(should_sell_raw)
        score = scores.get("should_sell") if scores else None

    trace = _build_evaluation_result(
        symbol=symbol,
        market_data={
            "entry_price": entry_price,
            "current_price": current_price,
            "pnl_percent": round(pnl_percent, 2),
            "binance_context": binance_context.model_dump(),
        },
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "symbol": symbol,
        "decision": decision,
        "score": score,
        "entry_price": entry_price,
        "current_price": current_price,
        "pnl_percent": round(pnl_percent, 2),
        "trace": trace,
    }
