"""Application configuration module."""
import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from a local .env file (if present).
load_dotenv()


# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Trial Configuration
MAX_TRIAL_DURATION_HOURS = int(os.getenv("MAX_TRIAL_DURATION_HOURS", "24"))
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "100"))

# LLM Configuration
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# Session Configuration
SESSION_COOKIE_SECURE = FLASK_ENV == "production"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = 3600 * MAX_TRIAL_DURATION_HOURS  # In seconds
