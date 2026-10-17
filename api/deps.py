"""Dependencies de FastAPI."""
from typing import Optional
from fastapi import Header, HTTPException

from config import API_SECRET_KEY


def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verifica la API Key en el header Authorization."""
    if not authorization or authorization != f"Bearer {API_SECRET_KEY}":
        raise HTTPException(
            status_code=401,
            detail="No autorizado: API Key inválida o no provista",
        )
    return True
