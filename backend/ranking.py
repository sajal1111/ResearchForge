"""
Pure-Python, rule-based source ranking. No LLM involved.

Scoring is a weighted sum of:
- domain quality  (heuristic allow/deny lists + TLD signal)
- keyword overlap  (query terms present in title/snippet)
- freshness        (best-effort year detection in snippet/title)

Dedup collapses near-identical URLs (trailing slashes, query strings, www.).
"""

import re
from urllib.parse import urlparse
from datetime import datetime

# Domains that tend to produce reliable, citable content.
# Not exhaustive by design -- this is a light nudge, not a whitelist gate.
HIGH_QUALITY_DOMAINS = {
    "wikipedia.org", "nature.com", "sciencedirect.com", "arxiv.org",
    "gov", "edu", "reuters.com", "apnews.com", "bbc.com", "nytimes.com",
    "ieee.org", "acm.org", "who.int", "un.org",
}

# Domains that are usually low-signal for research reports.
LOW_QUALITY_DOMAINS = {
    "pinterest.com", "quora.com", "answers.com", "slideshare.net",
}


def parse_search_results(raw: str) -> list[dict]:
    """
    Parse the string format produced by tools.web_search back into a list of
    {title, url, snippet} dicts, so ranking can work on structured data without
    changing the existing tool's return type.
    """
    entries = []
    blocks = raw.split("\n----\n")

    for block in blocks:
        title_match = re.search(r"Title:\s*(.+)", block)
        url_match = re.search(r"URL:\s*(\S+)", block)
        snippet_match = re.search(r"Snippet:\s*(.+)", block, re.DOTALL)

        if not url_match:
            continue

        entries.append({
            "title": title_match.group(1).strip() if title_match else "",
            "url": url_match.group(1).strip(),
            "snippet": snippet_match.group(1).strip() if snippet_match else "",
        })

    return entries


def normalize_url(url: str) -> str:
    """Collapse trivially-different URLs to the same key for dedup purposes."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"


def dedupe(sources: list[dict]) -> list[dict]:
    """Remove sources whose normalized URL has already been seen."""
    seen = set()
    deduped = []

    for source in sources:
        key = normalize_url(source["url"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(source)

    return deduped


def score_domain(url: str) -> float:
    """Score 0.0-1.0 based on domain reputation heuristics."""
    netloc = urlparse(url).netloc.lower().removeprefix("www.")

    if any(netloc.endswith(d) for d in HIGH_QUALITY_DOMAINS):
        return 1.0
    if any(netloc.endswith(d) for d in LOW_QUALITY_DOMAINS):
        return 0.1
    if netloc.endswith(".gov") or netloc.endswith(".edu"):
        return 1.0

    return 0.5  # neutral default for unknown domains


def score_relevance(source: dict, query_terms: list[str]) -> float:
    """Score 0.0-1.0 based on query keyword overlap in title + snippet."""
    if not query_terms:
        return 0.5

    text = f"{source.get('title', '')} {source.get('snippet', '')}".lower()
    hits = sum(1 for term in query_terms if term.lower() in text)

    return min(hits / len(query_terms), 1.0)


def score_freshness(source: dict) -> float:
    """
    Score 0.0-1.0 based on best-effort year detection in title/snippet.
    No date found -> neutral score, since absence isn't evidence of staleness.
    """
    text = f"{source.get('title', '')} {source.get('snippet', '')}"
    years = re.findall(r"\b(20[0-2][0-9])\b", text)

    if not years:
        return 0.5

    most_recent = max(int(y) for y in years)
    current_year = datetime.now().year
    age = current_year - most_recent

    if age <= 0:
        return 1.0
    if age == 1:
        return 0.8
    if age <= 3:
        return 0.5
    return 0.2


def rank_sources(
    sources: list[dict],
    query: str,
    weights: dict | None = None,
) -> list[dict]:
    """
    Dedupe and rank sources by weighted score. Returns sources sorted
    best-first, each with a `score` key attached.

    weights: optional override, e.g. {"domain": 0.5, "relevance": 0.3, "freshness": 0.2}
    """
    weights = weights or {"domain": 0.4, "relevance": 0.4, "freshness": 0.2}
    query_terms = [t for t in re.split(r"\s+", query) if len(t) > 2]

    deduped = dedupe(sources)

    scored = []
    for source in deduped:
        domain_score = score_domain(source["url"])
        relevance_score = score_relevance(source, query_terms)
        freshness_score = score_freshness(source)

        total = (
            domain_score * weights["domain"]
            + relevance_score * weights["relevance"]
            + freshness_score * weights["freshness"]
        )

        scored.append({**source, "score": round(total, 3)})

    return sorted(scored, key=lambda s: s["score"], reverse=True)