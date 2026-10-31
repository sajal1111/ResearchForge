"""
FastAPI application factory.

Wires together:
  - CORS middleware (origins from ALLOWED_ORIGINS env var)
  - Global exception handler (prevents raw tracebacks reaching clients)
  - /health endpoint (for Render/Railway health checks)
  - /research router
  - OpenAPI docs at /docs (FastAPI default — not disabled)
"""

from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routers.research import router as research_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "ResearchForge API — Forge reliable research from the web using intelligent AI agents. "
        "POST /research to generate a report; GET /health for uptime checks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
logger.info("CORS allowed origins: %s", settings.cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global exception handler
# Catches any unhandled exception from the pipeline or service layer and
# returns a clean JSON 500 — no raw tracebacks leak to the client.
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s:\n%s", request.method, request.url, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": (
                f"{type(exc).__name__}: {exc}" if settings.DEBUG
                else "An internal error occurred. Please try again later."
            ),
        },
    )

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["infra"], summary="Health check for Render/Railway")
async def health() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(research_router)

logger.info("FastAPI app '%s' v%s ready.", settings.APP_TITLE, settings.APP_VERSION)
