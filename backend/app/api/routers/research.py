"""
POST /research router.

IMPORTANT — plain def, NOT async def:
    run_research_pipeline() calls asyncio.run() internally (twice: once for
    parallel search, once for parallel scraping). Calling asyncio.run() from
    inside an already-running event loop (which FastAPI's async handlers run
    in) raises RuntimeError. Defining this route as a plain def causes FastAPI
    to dispatch it to a threadpool, where no outer event loop exists, so the
    pipeline's asyncio.run() calls work correctly.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research_service import run_research

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


@router.post(
    "",
    response_model=ResearchResponse,
    summary="Generate a research report",
    description=(
        "Run the full multi-agent research pipeline for a given topic and mode. "
        "Expects 20–90 seconds depending on topic complexity, source availability, "
        "and LLM rate limits. Set your HTTP client timeout ≥ 120 s."
    ),
)
def research(request: ResearchRequest) -> ResearchResponse:   # ← plain def (see module docstring)
    """
    Entry point for the research pipeline.

    FastAPI automatically dispatches sync route handlers to a threadpool,
    so the pipeline's internal asyncio.run() calls have no outer event loop
    to conflict with.
    """
    logger.info("Research request received: topic=%r mode=%s", request.topic, request.mode)

    try:
        response = run_research(topic=request.topic, mode=request.mode)
    except ValueError as exc:
        # Bad input that slipped past Pydantic (shouldn't normally happen).
        logger.warning("Validation error in pipeline: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Let the global handler in main.py produce the 500 response;
        # re-raise so the handler sees the original exception.
        logger.exception("Pipeline failed for topic=%r: %s", request.topic, exc)
        raise

    logger.info("Research complete: topic=%r report_length=%d", request.topic, len(response.report))
    return response
