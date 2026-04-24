"""Shared async HTTP fetcher with per-scan memoisation."""

from __future__ import annotations

import httpx

_TIMEOUT = httpx.Timeout(15, connect=10)
_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (compatible; AISEOBot/1.0; +https://github.com/LindaHaviv/aiseo)"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class Fetcher:
    """Cache HTTP responses within a single scan so repeated URLs are fetched once."""

    def __init__(self) -> None:
        self._cache: dict[str, httpx.Response] = {}
        self._client = httpx.AsyncClient(
            timeout=_TIMEOUT,
            headers=_HEADERS,
            follow_redirects=True,
            max_redirects=5,
        )

    async def get(self, url: str) -> httpx.Response:
        if url in self._cache:
            return self._cache[url]
        resp = await self._client.get(url)
        self._cache[url] = resp
        return resp

    async def head(self, url: str) -> httpx.Response:
        key = f"HEAD:{url}"
        if key in self._cache:
            return self._cache[key]
        resp = await self._client.head(url)
        self._cache[key] = resp
        return resp

    async def close(self) -> None:
        await self._client.aclose()
