"""FastAPI entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import buy_router, exit_router, health_router, signal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events para startup/shutdown."""
    from services import get_router
    print("Cargando modelo Laya...")
    get_router()
    print("¡Laya listo para tomar decisiones de trading!")
    yield
    print("Apagando...")


app = FastAPI(
    title="Trading Decision API - Laya",
    description="API de decisiones de trading con Laya para evaluar entradas y salidas",
    lifespan=lifespan,
)

# CORS para permitir peticiones desde múltiples localhosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Frontend local
        "http://localhost:3001",      # Frontend local alternativo
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(buy_router)
app.include_router(exit_router)
app.include_router(signal_router)
app.include_router(health_router)
