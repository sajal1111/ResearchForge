"""Centralized constants. Expanded incrementally as new steps need new settings."""

from pathlib import Path

# --- Cache ---
CACHE_DIR = Path(".cache")
SEARCH_CACHE_TTL_SECONDS = 60 * 60 * 6     # 6 hours -- search results go stale fast
PAGE_CACHE_TTL_SECONDS = 60 * 60 * 24 * 3  # 3 days -- page content is more stable
# --- Planner ---
SUBTOPIC_COUNT = 3
# --- Scraping ---
TOP_N_SOURCES_TO_SCRAPE = 3
# --- Report modes ---
DEFAULT_REPORT_MODE = "deep_research"
# --- Summarization ---
SUMMARY_TARGET_WORDS = 150