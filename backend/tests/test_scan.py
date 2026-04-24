"""Tests for the /api/scan endpoint with mocked HTTP responses."""

from __future__ import annotations

import pytest
import respx
from httpx import AsyncClient, Response

MOCK_HTML = (
    "<!DOCTYPE html><html lang='en'><head>"
    "<title>Test Site - AI-Friendly Example</title>"
    '<meta name="description" content="A test site for AI SEO scanning.">'
    '<meta property="og:title" content="Test Site">'
    '<meta property="og:description" content="AI-friendly example">'
    '<meta property="og:image" content="https://example.com/og.png">'
    '<link rel="canonical" href="https://example.com/">'
    '<script type="application/ld+json">'
    '{"@context":"https://schema.org","@type":"WebSite",'
    '"name":"Test Site","url":"https://example.com"}</script>'
    "</head><body><header><nav>Navigation</nav></header><main>"
    "<article><h1>Welcome to Test Site</h1>"
    "<section><h2>About Us</h2>"
    "<p>Long paragraph with meaningful content for ratio. "
    "We provide excellent services that help grow. "
    "Our team delivers outstanding results.</p></section>"
    "<section><h2>Services</h2>"
    "<p>We offer web development and AI consulting.</p>"
    "</section></article></main>"
    "<footer>Footer content here</footer></body></html>"
)

MOCK_ROBOTS = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

Sitemap: https://example.com/sitemap.xml
"""

MOCK_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
</urlset>"""

MOCK_LLMS_TXT = """# Test Site

> A comprehensive test site for AI SEO validation.

## Pages
- [Home](/): Main landing page
- [About](/about): About us
"""


@respx.mock
@pytest.mark.asyncio
async def test_scan_high_score(client: AsyncClient):
    """A well-optimised site should score high."""
    respx.get("https://example.com/").mock(
        return_value=Response(200, text=MOCK_HTML, headers={"content-type": "text/html"})
    )
    respx.get("https://example.com/robots.txt").mock(
        return_value=Response(200, text=MOCK_ROBOTS, headers={"content-type": "text/plain"})
    )
    respx.get("https://example.com/sitemap.xml").mock(
        return_value=Response(200, text=MOCK_SITEMAP, headers={"content-type": "application/xml"})
    )
    respx.get("https://example.com/llms.txt").mock(
        return_value=Response(200, text=MOCK_LLMS_TXT, headers={"content-type": "text/plain"})
    )
    respx.get("https://example.com/llms-full.txt").mock(return_value=Response(404))

    resp = await client.post("/api/scan", json={"url": "https://example.com"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["url"] == "https://example.com"
    assert data["score"] >= 70
    assert data["grade"] in ("A", "B")
    assert len(data["categories"]) >= 3
    assert isinstance(data["fixes"], list)
    assert data["scanned_at"]


@respx.mock
@pytest.mark.asyncio
async def test_scan_low_score(client: AsyncClient):
    """A bare-bones site should score low and get many fixes."""
    bare_html = "<html><body><div>Hello</div></body></html>"
    respx.get("https://bad-site.com/").mock(
        return_value=Response(200, text=bare_html, headers={"content-type": "text/html"})
    )
    respx.get("https://bad-site.com/robots.txt").mock(return_value=Response(404))
    respx.get("https://bad-site.com/sitemap.xml").mock(return_value=Response(404))
    respx.get("https://bad-site.com/sitemap_index.xml").mock(return_value=Response(404))
    respx.get("https://bad-site.com/llms.txt").mock(return_value=Response(404))
    respx.get("https://bad-site.com/llms-full.txt").mock(return_value=Response(404))

    resp = await client.post("/api/scan", json={"url": "https://bad-site.com"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["score"] < 50
    assert data["grade"] in ("D", "F")
    assert len(data["fixes"]) >= 5


@respx.mock
@pytest.mark.asyncio
async def test_scan_blocked_bots(client: AsyncClient):
    """A site blocking AI bots should flag it."""
    blocking_robots = "User-agent: GPTBot\nDisallow: /\n"
    respx.get("https://blocked.com/").mock(
        return_value=Response(
            200,
            text=(
                "<html><head><title>Blocked Site</title></head>"
                "<body><main><h1>Hi</h1><p>Content</p>"
                "</main></body></html>"
            ),
            headers={"content-type": "text/html"},
        )
    )
    respx.get("https://blocked.com/robots.txt").mock(
        return_value=Response(200, text=blocking_robots)
    )
    respx.get("https://blocked.com/sitemap.xml").mock(return_value=Response(404))
    respx.get("https://blocked.com/sitemap_index.xml").mock(return_value=Response(404))
    respx.get("https://blocked.com/llms.txt").mock(return_value=Response(404))
    respx.get("https://blocked.com/llms-full.txt").mock(return_value=Response(404))

    resp = await client.post("/api/scan", json={"url": "https://blocked.com"})
    data = resp.json()

    bot_fix_ids = [f["check_id"] for f in data["fixes"]]
    assert "robots_ai_bots" in bot_fix_ids


@pytest.mark.asyncio
async def test_scan_invalid_url(client: AsyncClient):
    """Invalid URL should return 422."""
    resp = await client.post("/api/scan", json={"url": "not-a-url"})
    assert resp.status_code == 422
