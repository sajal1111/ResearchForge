"""
Pydantic v2 schemas for the /research API endpoint.

These mirror the pipeline's output dict exactly so the service layer
can map pipeline results → response without lossy transformations.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Allowed report mode values — must stay in sync with report_modes.py
# ---------------------------------------------------------------------------
ReportMode = Literal[
    "quick_summary",
    "deep_research",
    "technical",
    "business",
    "interview_prep",
]


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300, description="Research topic or question")
    mode: ReportMode = Field(default="deep_research", description="Report style / depth")

    model_config = {"json_schema_extra": {"example": {"topic": "Quantum computing hardware in 2025", "mode": "deep_research"}}}


# ---------------------------------------------------------------------------
# Response sub-models
# ---------------------------------------------------------------------------
class SourceItem(BaseModel):
    url: str = Field(..., description="Source URL")
    title: str | None = Field(None, description="Page title from search results")
    snippet: str | None = Field(None, description="Short excerpt from search result")
    score: float | None = Field(None, description="Heuristic relevance score (0-1, relative, not absolute quality)")


class CriticReview(BaseModel):
    """
    Structured parse of the critic chain's plain-text output.
    All structured fields may be None/empty if parsing fails —
    the `raw` field is always included as the authoritative fallback.
    """
    score: str | None = Field(None, description="e.g. '7/10' — kept as string, not forced to int")
    strengths: list[str] = Field(default_factory=list, description="Bullet points from Strengths section")
    weaknesses: list[str] = Field(default_factory=list, description="Bullet points from Areas to Improve section")
    verdict: str | None = Field(None, description="One-line verdict from the critic")
    raw: str = Field(..., description="Full raw critic text — always present as fallback")


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------
class ResearchResponse(BaseModel):
    report: str = Field(..., description="Final markdown research report")
    critic: CriticReview
    sources: list[SourceItem]
    mode: ReportMode
    topic: str
