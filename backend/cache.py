"""
Lightweight cache for search results and scraped pages.

Design:
- In-memory dict for the lifetime of the process (fast, no I/O per lookup).
- Flat JSON file on disk so the cache survives restarts (no Redis/DB).
- TTL is checked on read; expired entries are treated as misses and
  overwritten on the next write.
- This module wraps AROUND calls to tools.web_search / tools.scrape_url --
  it does not modify those tools. Caching is a pipeline-level concern.
"""

import json
import time
import hashlib
from pathlib import Path
from config import CACHE_DIR, SEARCH_CACHE_TTL_SECONDS, PAGE_CACHE_TTL_SECONDS

SEARCH_CACHE_FILE = CACHE_DIR / "search_cache.json"
PAGE_CACHE_FILE = CACHE_DIR / "page_cache.json"


def _make_key(value: str) -> str:
    """Hash long/irregular strings (queries, URLs) into a safe fixed-length key."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class FlatFileCache:
    """A dict-backed cache that persists to a single JSON file."""

    def __init__(self, path: Path, ttl_seconds: int):
        self.path = path
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, dict] = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable cache file -- start fresh rather than crash.
            return {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._store, f)

    def get(self, raw_key: str) -> str | None:
        key = _make_key(raw_key)
        entry = self._store.get(key)

        if entry is None:
            return None

        age = time.time() - entry["timestamp"]
        if age > self.ttl_seconds:
            return None  # expired -- treated as a miss, not deleted here

        return entry["value"]

    def set(self, raw_key: str, value: str) -> None:
        key = _make_key(raw_key)
        self._store[key] = {"value": value, "timestamp": time.time()}
        self._save()


search_cache = FlatFileCache(SEARCH_CACHE_FILE, SEARCH_CACHE_TTL_SECONDS)
page_cache = FlatFileCache(PAGE_CACHE_FILE, PAGE_CACHE_TTL_SECONDS)


def cached_web_search(web_search_tool, query: str) -> str:
    """Call web_search through the cache. Falls through to the tool on a miss."""
    hit = search_cache.get(query)
    if hit is not None:
        print(f"[cache] search hit: {query}")
        return hit

    result = web_search_tool.invoke({"query": query})
    search_cache.set(query, result)
    return result


def cached_scrape_url(scrape_url_tool, url: str) -> str:
    """Call scrape_url through the cache. Falls through to the tool on a miss."""
    hit = page_cache.get(url)
    if hit is not None:
        print(f"[cache] page hit: {url}")
        return hit

    result = scrape_url_tool.invoke({"url": url})
    page_cache.set(url, result)
    return result