"""Routes package."""
from .buy import router as buy_router
from .exit import router as exit_router
from .health import router as health_router
from .signal import router as signal_router

__all__ = ["buy_router", "exit_router", "health_router", "signal_router"]
