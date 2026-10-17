"""Configuración global del proyecto."""
import os
from dotenv import load_dotenv

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "default_dev_key")
MODEL_PRELOAD = os.getenv("MODEL_PRELOAD", "true").lower() == "true"
