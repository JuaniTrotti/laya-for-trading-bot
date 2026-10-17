"""Templates de preguntas para Laya."""


def build_signal_confirmation_questions(strategy_rules: str, ticker: str, price: float) -> dict:
    return {
        "should_buy": {
            "type": "noul",
            "instructions": (
                f"TradingView triggered a BUY_SIGNAL for {ticker} at ${price}. "
                "Analyze ALL available data: TradingView scores (structure, volume, RSI, trend), "
                "Binance order flow (volume delta, buyer/seller dominance), "
                "derivatives (open interesst, long/short ratio, funding rate), "
                "order book (spread, liquidity), and BTC context. "
                f"Should we BUY? Answer TRUE to execute the trade, FALSE to reject. "
                f"Consider these rules: {strategy_rules}"
            ),
        }
    }


def build_exit_questions(strategy_rules: str, symbol: str, entry_price: float, current_price: float, pnl_percent: float) -> dict:
    return {
        "should_sell": {
            "type": "noul",
            "instructions": (
                f"Position: {symbol} | Entry: ${entry_price} | Current: ${current_price} | PnL: {pnl_percent}%. "
                "Analyze ALL available data: Binance order flow (volume delta, buyer/seller dominance), "
                "derivatives (open interest, long/short ratio, funding rate), "
                "order book (spread, liquidity), and BTC context. "
                f"Should we SELL and exit the position? Answer TRUE to exit, FALSE to hold. "
                f"Consider these rules: {strategy_rules}"
            ),
        }
    }