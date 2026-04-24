"""Shared async HTTP fetcher with per-scan memoisation and SSRF protection."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

_TIMEOUT = httpx.Timeout(15, connect=10)
_MAX_REDIRECTS = 5
_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (compatible; AISEOBot/1.0; +https://github.com/LindaHaviv/aiseo)"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _is_safe_url(url: str) -> bool:
    """Reject URLs targeting private/reserved IP ranges."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return False

    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    for _family, _type, _proto, _canonname, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_reserved or ip.is_loopback or ip.is_link_local:
            return False

    return True


class SSRFError(Exception):
    """Raised when a URL targets a private/reserved address."""


class Fetcher:
    """Cache HTTP responses within a single scan so repeated URLs are fetched once."""

    def __init__(self) -> None:
        self._cache: dict[str, httpx.Response] = {}
        self._client = httpx.AsyncClient(
            timeout=_TIMEOUT,
            headers=_HEADERS,
            follow_redirects=False,
        )

    def _validate(self, url: str) -> None:
        if not _is_safe_url(url):
            raise SSRFError(f"Blocked request to private/reserved address: {url}")

    async def _request(self, method: str, url: str) -> httpx.Response:
        """Issue a request, manually following redirects with SSRF validation."""
        self._validate(url)
        for _ in range(_MAX_REDIRECTS):
            resp = await self._client.request(method, url)
            if resp.is_redirect and resp.has_redirect_location:
                url = str(resp.url.join(resp.headers["location"]))
                self._validate(url)
            else:
                return resp
        return resp

    async def get(self, url: str) -> httpx.Response:
        if url in self._cache:
            return self._cache[url]
        resp = await self._request("GET", url)
        self._cache[url] = resp
        return resp

    async def head(self, url: str) -> httpx.Response:
        key = f"HEAD:{url}"
        if key in self._cache:
            return self._cache[key]
        resp = await self._request("HEAD", url)
        self._cache[key] = resp
        return resp

    async def close(self) -> None:
        await self._client.aclose()
