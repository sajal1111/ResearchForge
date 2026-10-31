"""
Research service layer.

Responsibilities:
  1. Call run_research_pipeline(topic, mode) — the black-box pipeline entry point.
  2. Parse the critic's plain-text output into structured fields.
  3. Map the raw pipeline dict → ResearchResponse schema.

⚠️  COUPLING POINT — critic text parsing:
    The parse_critic_text() function relies on the prompt format defined in
    critic_prompt inside agents.py. If you change that prompt's section
    headings (e.g., rename "Areas to Improve" or "One line verdict"), the
    regex patterns here will stop matching and the structured fields will
    silently fall back to empty lists / None. Update both files together.

    Current expected format (as of agents.py v1):
        Score: X/10

        Strengths:
        - ...

        Areas to Improve:
        - ...

        One line verdict:
        ...
"""

from __future__ import annotations

import re
import sys
import os
import logging
from contextlib import contextmanager, nullcontext
from typing import Generator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup — pipeline files live at backend/ root, one level above app/
# ---------------------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from pipeline import run_research_pipeline  # noqa: E402  (path setup must precede this)
from app.schemas.research import CriticReview, ResearchResponse, SourceItem

# ---------------------------------------------------------------------------
# LangSmith parent-trace helper
#
# LangChain already has built-in LangSmith integration: when LANGSMITH_TRACING=true
# and LANGSMITH_API_KEY are set, every chain invocation (planner_chain, writer_chain,
# critic_chain, summarizer_chain) is automatically recorded as a child run.
#
# This helper adds a *parent* run that groups all of those child runs from one
# API request into a single trace, and attaches the required tags.
#
# Design choices:
#   • Imported lazily so the app starts correctly even when langsmith is not installed.
#   • Falls back to nullcontext() when tracing is disabled or the key is missing.
#   • Does NOT modify any pipeline file — the wrapper lives here in the service layer.
# ---------------------------------------------------------------------------

@contextmanager
def _langsmith_parent_trace(topic: str, mode: str) -> Generator[None, None, None]:
    """
    Context manager that wraps the pipeline call in a LangSmith parent trace.

    Tags attached to every trace:
        project=ResearchForge
        provider=openrouter   (writer LLM) / mistralai (light LLM)
        model=gpt-oss-120b / mistral-small-2506
        report_mode=<mode>

    When LANGSMITH_TRACING is not 'true' or langsmith is not installed,
    yields immediately without doing anything.
    """
    tracing_enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
    api_key_present = bool(os.getenv("LANGSMITH_API_KEY", "").strip())

    if not (tracing_enabled and api_key_present):
        yield  # tracing off — no-op
        return

    try:
        from langsmith import trace as ls_trace  # lazy import
    except ImportError:
        logger.warning("langsmith package not installed — tracing disabled.")
        yield
        return

    project = os.getenv("LANGSMITH_PROJECT", "ResearchForge")
    tags = [
        "project=ResearchForge",
        "provider=openrouter",         # writer_chain uses ChatOpenRouter
        "provider=mistralai",          # planner/summarizer/critic use ChatMistralAI
        "model=gpt-oss-120b",          # writer model (agents.py: llm)
        "model=mistral-small-2506",    # light model (agents.py: light_llm)
        f"report_mode={mode}",
    ]

    with ls_trace(
        name="ResearchForge.run_research_pipeline",
        project_name=project,
        tags=tags,
        metadata={"topic": topic, "mode": mode},
    ):
        yield


# ---------------------------------------------------------------------------
# Critic text parser
# ---------------------------------------------------------------------------

def parse_critic_text(raw: str) -> CriticReview:
    """
    Parse the critic chain's plain-text output into a CriticReview.

    Uses section-splitting rather than a second LLM call — the format is
    prompt-defined and stable enough for regex. All fields fall back
    gracefully so a malformed critic response never crashes the endpoint.

    Args:
        raw: Full raw string from critic_chain output.

    Returns:
        CriticReview with structured fields + the raw text as fallback.
    """
    if not raw or not raw.strip():
        return CriticReview(raw=raw or "")

    score: str | None = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    verdict: str | None = None

    # --- Score: "Score: 7/10" or "Score: 7 / 10" ---
    score_match = re.search(r"Score\s*:\s*(\d+\s*/\s*10)", raw, re.IGNORECASE)
    if score_match:
        # Normalise spacing: "7 / 10" → "7/10"
        score = re.sub(r"\s*\/\s*", "/", score_match.group(1).strip())

    # --- Extract bullet lists from named sections ---
    def _extract_bullets(section_pattern: str) -> list[str]:
        """
        Find a section by its header regex, then collect all '- ...' bullets
        until the next section or end of string.
        """
        section_match = re.search(section_pattern, raw, re.IGNORECASE)
        if not section_match:
            return []
        start = section_match.end()
        # Everything after the header until a blank line followed by a
        # non-bullet word (i.e., the next section header), or end of string.
        chunk = raw[start:]
        # Stop at the next section-like header (a line that ends with ':')
        next_header = re.search(r"\n[A-Za-z][^\n]+:\s*\n", chunk)
        if next_header:
            chunk = chunk[: next_header.start()]
        bullets = re.findall(r"^\s*[-*•]\s*(.+)", chunk, re.MULTILINE)
        return [b.strip() for b in bullets if b.strip()]

    strengths = _extract_bullets(r"Strengths\s*:")
    weaknesses = _extract_bullets(r"Areas\s+to\s+Improve\s*:|Weaknesses\s*:|Areas\s+for\s+Improvement\s*:")

    # --- One line verdict: everything after "One line verdict:" ---
    verdict_match = re.search(r"One\s+line\s+verdict\s*:\s*(.+)", raw, re.IGNORECASE | re.DOTALL)
    if verdict_match:
        # Take only the first non-empty line
        verdict_text = verdict_match.group(1).strip()
        verdict = verdict_text.splitlines()[0].strip() if verdict_text else None

    return CriticReview(
        score=score,
        strengths=strengths,
        weaknesses=weaknesses,
        verdict=verdict,
        raw=raw,
    )


# ---------------------------------------------------------------------------
# Main service function
# ---------------------------------------------------------------------------

def run_research(topic: str, mode: str) -> ResearchResponse:
    """
    Orchestrate the pipeline call and map its output to ResearchResponse.

    This function is called from a plain-def FastAPI route handler (not async),
    which means it runs in FastAPI's threadpool — safe for the pipeline's
    internal asyncio.run() calls.

    Args:
        topic: The research topic string (validated upstream by Pydantic).
        mode:  One of the five ReportMode literals.

    Returns:
        ResearchResponse — fully typed, ready for FastAPI to serialise.

    Raises:
        RuntimeError: Propagated from the pipeline on unrecoverable failures.
                      The FastAPI global exception handler converts this to a
                      clean 500 JSON response.
    """
    # Pipeline runs synchronously inside a LangSmith parent trace (no-op when tracing is off).
    with _langsmith_parent_trace(topic=topic, mode=mode):
        result: dict = run_research_pipeline(topic=topic, mode=mode)

    # --- Map ranked_sources → list[SourceItem] ---
    # ranked_sources items: {title, url, snippet, score}  (all from ranking.py)
    raw_sources: list[dict] = result.get("ranked_sources", [])
    sources = [
        SourceItem(
            url=s.get("url", ""),
            title=s.get("title") or None,
            snippet=s.get("snippet") or None,
            score=s.get("score"),
        )
        for s in raw_sources
        if s.get("url")  # skip malformed entries without a URL
    ]

    # --- Parse critic text ---
    raw_feedback: str = result.get("feedback", "")
    critic = parse_critic_text(raw_feedback)

    return ResearchResponse(
        report=result.get("report", ""),
        critic=critic,
        sources=sources,
        mode=mode,  # type: ignore[arg-type]  — validated as ReportMode by upstream schema
        topic=topic,
    )
