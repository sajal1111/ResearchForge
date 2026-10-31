"""
API-layer configuration — completely separate from the pipeline's config.py.

The pipeline's config.py (backend/config.py) holds pipeline constants like
SUBTOPIC_COUNT, cache TTLs, etc. and is imported directly by the pipeline
modules. THIS file handles only API/deployment settings loaded via
pydantic-settings from environment variables.

Do NOT merge these two files. The pipeline imports `config` (the root-level
one) by name; renaming it would break every pipeline module.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------ CORS
    # Comma-separated list of allowed frontend origins.
    # Local dev default: Vite dev server.
    # Production: set ALLOWED_ORIGINS=https://your-app.vercel.app in Render/Railway.
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # ------------------------------------------------------------------ App
    APP_TITLE: str = "ResearchForge API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ------------------------------------------------------------------ Uvicorn (informational only — uvicorn reads $PORT directly)
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars (pipeline keys, etc.)
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS into a list (strips whitespace around commas)."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
