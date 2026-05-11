"""
Shared WebSearch helper for evolution loop strands.

All cloud-callable. Uses DuckDuckGo Lite HTML scrape (no API key needed).
Returns None on any failure so strands can fall back to pre-banked menu.

Usage:
    from strands.websearch import search_first_result
    signal = search_first_result("Cafe24 API changes 2026")
    if signal:
        # signal = {"title": ..., "snippet": ..., "url": ..., "query": ...}
"""

import sys
import re
import urllib.request
import urllib.parse
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}
_TIMEOUT = 10  # seconds


def search_first_result(query: str) -> dict | None:
    """
    Run a single DuckDuckGo Lite search. Return the first result or None.

    Returns dict with keys: title, snippet, url, query
    Returns None if network error, no results, or parse failure.
    """
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://lite.duckduckgo.com/lite/?q={encoded}"
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None

    # DuckDuckGo Lite: results are in <a class="result-link"> tags
    # Snippet text follows in a <td class="result-snippet">
    titles = re.findall(r'class="result-link"[^>]*>([^<]+)<', html)
    snippets = re.findall(r'class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
    urls = re.findall(r'class="result-link"\s+href="([^"]+)"', html)

    # Strip tags from snippets
    def strip_tags(s: str) -> str:
        return re.sub(r"<[^>]+>", "", s).strip()

    if not titles:
        return None

    title = titles[0].strip()
    snippet = strip_tags(snippets[0]) if snippets else ""
    url = urls[0] if urls else ""

    # Basic freshness filter: skip if snippet has no year signal >= 2025
    year_hits = re.findall(r"20(2[5-9]|3\d)", snippet + title)
    if not year_hits and snippet:
        # No recent year mentioned, treat as stale
        return None

    return {
        "title": title,
        "snippet": snippet[:300],
        "url": url,
        "query": query,
    }


def search_any(queries: list[str]) -> dict | None:
    """
    Try each query in order. Return first non-None result or None.
    """
    for q in queries:
        result = search_first_result(q)
        if result:
            return result
    return None
