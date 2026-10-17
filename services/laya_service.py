"""Servicio de Laya para inferencia."""
from typing import Dict, Any, Optional, List

from laya import Router

from config import MODEL_PRELOAD
from models.market import (
    BinanceMarketState,
    PositionState,
    TradingViewSignalData,
    BinanceContext,
)
from models.responses import (
    EvaluationInput,
    EvaluationResult,
    QuestionItem,
    AnswerItem,
)
from .question_templates import (
    build_buy_questions,
    build_exit_questions,
    build_signal_confirmation_questions,
)


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

def build_laya_state(market_data: BinanceMarketState, custom_rules: Optional[str]) -> Dict[str, str]:
    """Convierte market data genérico al formato de estado que espera Laya."""
    strategy_rules = custom_rules or "Estrategia general de trading spot"

    return {
        "symbol": market_data.symbol,
        "current_price": f"${market_data.price}",
        "price_change_24h": f"{market_data.change_24h_percent}%",
        "volume_24h": f"${market_data.volume_24h_usdt:,.2f} USDT",
        "rsi_14": str(market_data.rsi_14) if market_data.rsi_14 else "N/A",
        "technical_context": market_data.trend_description or "Sin contexto adicional",
        "strategy_rules": strategy_rules,
    }


def build_laya_state_with_position(
    market_data: BinanceMarketState,
    position_data: PositionState,
    custom_rules: Optional[str],
) -> Dict[str, str]:
    """Convierte market data + position data al formato de estado para Laya (decisión de salida)."""
    state = build_laya_state(market_data, custom_rules)
    state.update({
        "entry_price": f"${position_data.entry_price}",
        "current_pnl": f"{position_data.pnl_percent}%",
        "holding_time": position_data.holding_time or "N/A",
        "stop_loss_price": f"${position_data.stop_loss_price}" if position_data.stop_loss_price else "N/A",
    })
    return state


def build_laya_state_from_signal(
    tradingview_data: TradingViewSignalData,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, str]:
    """
    Construye el state completo para Laya a partir de la señal de TradingView
    y el contexto de Binance (para decisión de COMPRA).
    """
    tv = tradingview_data
    bc = binance_context

    # Calcular Risk/Reward ratio (si vienen stop_loss y take_profit)
    if tv.stop_loss and tv.take_profit:
        risk = tv.price - tv.stop_loss
        reward = tv.take_profit - tv.price
        rr_ratio = reward / risk if risk > 0 else 0
    else:
        rr_ratio = 0.0

    # Resumen de order flow
    order_flow_summary = (
        f"Volume Delta: {bc.order_flow.volume_delta:,.2f} "
        f"({'Buyer dominant' if bc.order_flow.buyer_dominance else 'Seller dominant'})"
    )

    # Resumen de derivados
    derivatives_summary = (
        f"OI: ${bc.derivatives.open_interest:,.2f}, "
        f"L/S Ratio: {bc.derivatives.top_long_short_ratio:.2f}, "
        f"Funding: {bc.derivatives.funding_rate:.6f}"
    )

    # BTC context
    btc_summary = (
        f"BTC: ${bc.btc_context.btc_price:,}, "
        f"5m change: {bc.btc_context.btc_5m_change_pct:.3f}%, "
        f"{'Stable/Bullish' if bc.btc_context.btc_is_stable_or_bullish else 'Bearish'}"
    )

    # Construir el state
    state = {
        # TradingView Signal
        "signal_type": tv.event,
        "signal_ticker": tv.ticker,
        "signal_price": f"${tv.price}",
        "signal_stop_loss": f"${tv.stop_loss}" if tv.stop_loss else "N/A",
        "signal_take_profit": f"${tv.take_profit}" if tv.take_profit else "N/A",
        "signal_score_total": str(tv.score_total),
        "signal_score_structure": str(tv.scores.structure),
        "signal_score_volume": str(tv.scores.volume),
        "signal_score_rsi": str(tv.scores.rsi),
        "signal_score_trend": str(tv.scores.trend),
        "signal_rr_ratio": f"{rr_ratio:.2f}",
        # TradingView Metrics
        "signal_vol_ratio": str(tv.metrics.vol_ratio),
        "signal_rsi": str(tv.metrics.rsi),
        "signal_atr": str(tv.metrics.atr),
        "signal_bb_width": str(tv.metrics.bb_width),
        "signal_is_squeezed": "YES" if tv.metrics.is_squeezed else "NO",
        # Binance Context
        "binance_order_flow": order_flow_summary,
        "binance_derivatives": derivatives_summary,
        "binance_order_book_spread": f"${bc.order_book.spread}",
        "binance_btc_context": btc_summary,
        # Custom rules
        "strategy_rules": custom_rules or "Estrategia general de trading",
    }

    return state


def build_laya_state_from_exit_check(
    symbol: str,
    entry_price: float,
    current_price: float,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, str]:
    """
    Construye el state completo para Laya a partir del request de CHECK_SELL
    y el contexto de Binance (para decisión de VENTA/monitoreo de posición).

    Este state incluye:
    - Datos de la posición (entry, current, PnL)
    - Contexto de Binance actualizado
    """
    bc = binance_context

    # Calcular PnL
    pnl_percent = ((current_price - entry_price) / entry_price) * 100
    pnl_emoji = "📈" if pnl_percent >= 0 else "📉"

    # Resumen de order flow
    order_flow_summary = (
        f"Volume Delta: {bc.order_flow.volume_delta:,.2f} "
        f"({'Buyer dominant' if bc.order_flow.buyer_dominance else 'Seller dominant'})"
    )

    # Resumen de derivados
    derivatives_summary = (
        f"OI: ${bc.derivatives.open_interest:,.2f}, "
        f"L/S Ratio: {bc.derivatives.top_long_short_ratio:.2f}, "
        f"Funding: {bc.derivatives.funding_rate:.6f}"
    )

    # BTC context
    btc_summary = (
        f"BTC: ${bc.btc_context.btc_price:,}, "
        f"5m change: {bc.btc_context.btc_5m_change_pct:.3f}%, "
        f"{'Stable/Bullish' if bc.btc_context.btc_is_stable_or_bullish else 'Bearish'}"
    )

    # Order book
    order_book_summary = (
        f"Bid: ${bc.order_book.best_bid}, Ask: ${bc.order_book.best_ask}, "
        f"Spread: ${bc.order_book.spread}, Liquidity next 1%: ${bc.order_book.ask_liquidity_next_1pct:,.2f}"
    )

    state = {
        # Position Info
        "position_symbol": symbol,
        "position_entry_price": f"${entry_price}",
        "position_current_price": f"${current_price}",
        "position_pnl_percent": f"{pnl_percent:.2f}%",
        "position_pnl_status": f"{pnl_emoji} {' PROFIT' if pnl_percent >= 0 else ' LOSS'}",
        # Binance Context
        "binance_order_flow": order_flow_summary,
        "binance_derivatives": derivatives_summary,
        "binance_order_book": order_book_summary,
        "binance_btc_context": btc_summary,
        # Custom rules
        "strategy_rules": custom_rules or "Estrategia general de trading",
    }

    return state


# ==============================================================================
# HELPERS
# ==============================================================================

def _build_question_items(questions: Dict[str, Any]) -> List[QuestionItem]:
    """Convierte el dict de preguntas en lista de QuestionItem."""
    items = []
    for key, config in questions.items():
        items.append(QuestionItem(
            key=key,
            type=config.get("type", "noul"),
            instructions=config.get("instructions", ""),
            criteria=config.get("criteria"),
        ))
    return items


def _build_answer_items(
    questions: Dict[str, Any],
    answers: Dict[str, Any],
    scores: Optional[Dict[str, float]] = None,
) -> List[AnswerItem]:
    """Convierte las respuestas de Laya en lista de AnswerItem."""
    items = []
    for key, question_config in questions.items():
        raw_answer = answers.get(key)

        # Extraer valor, score y reasoning de la respuesta
        answer_value = raw_answer
        score = scores.get(key) if scores else None
        reasoning = None

        if isinstance(raw_answer, dict):
            answer_value = raw_answer.get("value", raw_answer)
            score = raw_answer.get("score") or score
            reasoning = raw_answer.get("reasoning")

        items.append(AnswerItem(
            question_key=key,
            answer_value=answer_value,
            score=score,
            reasoning=reasoning,
        ))
    return items


def _build_evaluation_result(
    symbol: str,
    market_data: Dict[str, Any],
    position_data: Optional[Dict[str, Any]],
    laya_state: Dict[str, str],
    questions: Dict[str, Any],
    laya_raw_result: Dict[str, Any],
) -> EvaluationResult:
    """Construye el EvaluationResult completo con todo el trace."""
    answers = laya_raw_result.get("answers", {})
    scores = laya_raw_result.get("scores") or laya_raw_result.get("routing", {}).get("scores")

    return EvaluationResult(
        input_data=EvaluationInput(
            symbol=symbol,
            market_data=market_data,
            position_data=position_data,
            custom_rules=laya_state.get("strategy_rules"),
            laya_state=laya_state,
        ),
        questions=_build_question_items(questions),
        answers=_build_answer_items(questions, answers, scores),
        routing=laya_raw_result.get("routing"),
        decision={
            "answers": answers,
            "scores": scores,
        },
    )


def _extract_main_decision(
    answers: Dict[str, Any],
    scores: Optional[Dict[str, float]],
    main_key: str,
) -> tuple[bool, Optional[float]]:
    """Extrae la decisión principal (should_buy o should_exit)."""
    main_answer = answers.get(main_key)
    decision = False
    score = None

    if main_answer is not None:
        if isinstance(main_answer, dict):
            decision = bool(main_answer.get("value", main_answer))
            score = main_answer.get("score") or (scores.get(main_key) if scores else None)
        else:
            decision = bool(main_answer)
            score = scores.get(main_key) if scores else None

    return decision, score


# ==============================================================================
# PREDICT FUNCTIONS
# ==============================================================================

def predict_buy(market_data: BinanceMarketState, custom_rules: Optional[str]) -> Dict[str, Any]:
    """Ejecuta predicción de compra usando Laya (modo simple)."""
    router = get_router()
    laya_state = build_laya_state(market_data, custom_rules)
    questions = build_buy_questions(custom_rules or "")
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    should_buy, should_buy_score = _extract_main_decision(answers, scores, "should_buy")

    trace = _build_evaluation_result(
        symbol=market_data.symbol,
        market_data=market_data.model_dump(),
        position_data=None,
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "should_buy": should_buy,
        "should_buy_score": should_buy_score,
        "trace": trace,
    }


def predict_signal_confirmation(
    tradingview_data: TradingViewSignalData,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, Any]:
    """
    Ejecuta confirmación de señal de TradingView usando Laya.

    Laya recibe la alerta de TradingView + contexto de Binance
    y decide si CONFIRMA o RECHAZA la señal de compra.
    """
    router = get_router()
    laya_state = build_laya_state_from_signal(tradingview_data, binance_context, custom_rules)
    questions = build_signal_confirmation_questions(custom_rules or "")
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    # La pregunta principal es "confirm_signal"
    confirm_signal, confirm_score = _extract_main_decision(answers, scores, "confirm_signal")

    trace = _build_evaluation_result(
        symbol=tradingview_data.ticker,
        market_data=tradingview_data.model_dump(),
        position_data=None,
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "signal_confirmed": confirm_signal,
        "confirm_score": confirm_score,
        "signal_ticker": tradingview_data.ticker,
        "signal_event": tradingview_data.event,
        "signal_price": tradingview_data.price,
        "trace": trace,
    }


def predict_exit(
    market_data: BinanceMarketState,
    position_data: PositionState,
    custom_rules: Optional[str],
) -> Dict[str, Any]:
    """Ejecuta predicción de salida usando Laya (modo genérico con PositionState)."""
    router = get_router()
    laya_state = build_laya_state_with_position(market_data, position_data, custom_rules)
    questions = build_exit_questions(custom_rules or "")
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    should_exit, should_exit_score = _extract_main_decision(answers, scores, "should_exit")

    trace = _build_evaluation_result(
        symbol=market_data.symbol,
        market_data=market_data.model_dump(),
        position_data=position_data.model_dump(),
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "should_exit": should_exit,
        "should_exit_score": should_exit_score,
        "trace": trace,
    }


def predict_exit_check(
    symbol: str,
    entry_price: float,
    current_price: float,
    binance_context: BinanceContext,
    custom_rules: Optional[str],
) -> Dict[str, Any]:
    """
    Ejecuta check de salida usando Laya (monitoreo de posición cada 40 segundos).

    Laya recibe datos actualizados de la posición y contexto de Binance
    y decide si MANTENER o SALIR de la posición.
    """
    router = get_router()
    laya_state = build_laya_state_from_exit_check(
        symbol=symbol,
        entry_price=entry_price,
        current_price=current_price,
        binance_context=binance_context,
        custom_rules=custom_rules,
    )
    questions = build_exit_questions(custom_rules or "")
    laya_result = router.predict(laya_state, questions)

    answers = laya_result.get("answers", {})
    scores = laya_result.get("scores") or laya_result.get("routing", {}).get("scores")

    should_exit, should_exit_score = _extract_main_decision(answers, scores, "should_exit")

    # Calcular PnL para la respuesta
    pnl_percent = ((current_price - entry_price) / entry_price) * 100

    trace = _build_evaluation_result(
        symbol=symbol,
        market_data={
            "entry_price": entry_price,
            "current_price": current_price,
            "pnl_percent": round(pnl_percent, 2),
            "binance_context": binance_context.model_dump(),
        },
        position_data=None,
        laya_state=laya_state,
        questions=questions,
        laya_raw_result=laya_result,
    )

    return {
        "should_exit": should_exit,
        "should_exit_score": should_exit_score,
        "symbol": symbol,
        "entry_price": entry_price,
        "current_price": current_price,
        "pnl_percent": round(pnl_percent, 2),
        "trace": trace,
    }
