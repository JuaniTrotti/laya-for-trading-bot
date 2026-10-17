# Trading Decision API - Laya

API de decisiones de trading que usa Laya para evaluar entradas y salidas de posiciones.

## Requisitos

- Python 3.10+
- Laya model

## Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd test-laya-model

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API_SECRET_KEY
```

## Uso

```bash
# Iniciar el servidor
uvicorn app:app --reload --port 8000
```

## Endpoints

### POST `/v1/confirm-signal`

Confirma o rechaza una señal de TradingView para compra.

```json
{
  "tradingview_data": {
    "event": "BUY_SIGNAL",
    "ticker": "SOLUSDT",
    "price": 104.28,
    "score_total": 60,
    "scores": { "structure": 25, "volume": 0, "rsi": 25, "trend": 10 },
    "metrics": { "vol_ratio": 0.46, "rsi": 67.45, "atr": 0.14, "bb_width": 0.0063, "is_squeezed": true }
  },
  "binance_context": {
    "order_flow": { "buyer_taker_volume": 2927.3, "seller_taker_volume": 6781.74, "volume_delta": -3854.44, "buyer_dominance": false },
    "derivatives": { "open_interest": 8938804.37, "top_long_short_ratio": 2.3359, "funding_rate": 0.00001031 },
    "order_book": { "ask_liquidity_next_1pct": 213056.24, "best_bid": 104.36, "best_ask": 104.37, "spread": 0.01 },
    "btc_context": { "btc_price": 81704, "btc_5m_change_pct": -0.047, "btc_is_stable_or_bullish": true }
  }
}
```

### POST `/v1/check-sell`

Evalúa si salir de una posición abierta (monitoreo cada 40 segundos).

```json
{
  "action": "CHECK_SELL",
  "symbol": "SOLUSDT",
  "entry_price": 104.28,
  "current_price": 104.36,
  "binance_context": { ... }
}
```

### GET `/health`

Health check endpoint.

## Autenticación

Todos los endpoints (excepto `/health`) requieren header:

```
Authorization: Bearer {API_SECRET_KEY}
```

## Estructura del proyecto

```
test-laya-model/
├── app.py                    # FastAPI entry point
├── config/
│   └── settings.py          # Configuración
├── models/
│   ├── market.py            # Modelos de datos de mercado
│   ├── requests.py          # Request models
│   └── responses.py         # Response models
├── services/
│   ├── laya_service.py      # Lógica de inferencia
│   └── question_templates.py # Templates de preguntas
└── api/
    ├── deps.py              # Dependencies (auth)
    └── routes/             # Endpoints
```
