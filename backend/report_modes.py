"""
Prompt variants for different report styles. Each mode is a block of writing
instructions injected into the shared writer_chain prompt -- not a separate
chain, so all modes still go through one writer_chain call.
"""

REPORT_MODES = {
    "quick_summary": """Write a CONCISE summary, 150-250 words total.
Structure: 2-3 short paragraphs covering the most important points only.
No headers needed. Skip minor details -- prioritize the single most
important takeaway per paragraph.""",

    "deep_research": """Write a thorough report between 500-800 words.
Structure as: Introduction, Key Findings (minimum 3 well-explained points),
Conclusion, References. Be detailed, factual, and comprehensive.""",

    "technical": """Write a technical report aimed at an engineering/technical
audience, 400-700 words. Structure as: Overview, Technical Details
(architecture, mechanisms, methods, or specifications as relevant),
Limitations/Tradeoffs, References. Use precise terminology; assume the
reader has domain background. Avoid marketing language.""",

    "business": """Write a business-oriented report aimed at decision-makers,
400-700 words. Structure as: Executive Summary, Market/Business Implications,
Risks & Opportunities, Recommendation, References. Focus on impact, cost,
and strategic relevance over technical depth.""",

    "interview_prep": """Write interview preparation notes, 300-600 words.
Structure as: Key Facts to Know, Likely Questions & Strong Answers
(at least 3 Q&A pairs grounded in the research), Notable Points to Mention,
References. Write answers in a confident, concise, first-person-ready style.""",
}


def get_mode_instructions(mode: str) -> str:
    """
    Return the writing instructions for a given mode. Falls back to
    deep_research if an unknown mode is passed, so a bad mode string never
    breaks the pipeline.
    """
    return REPORT_MODES.get(mode, REPORT_MODES["deep_research"])