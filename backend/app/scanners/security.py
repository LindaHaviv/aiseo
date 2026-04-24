"""Check HTTPS and basic security headers relevant to AI trust."""

from __future__ import annotations

from urllib.parse import urlparse

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_security(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    parsed = urlparse(base_url)
    if parsed.scheme == "https":
        results.append(
            CheckResult(
                id="https",
                name="HTTPS enabled",
                category="Trust & Security",
                status=CheckStatus.PASS,
                message="Site uses HTTPS",
                score=100,
                weight=0.05,
            )
        )
    else:
        results.append(
            CheckResult(
                id="https",
                name="HTTPS enabled",
                category="Trust & Security",
                status=CheckStatus.FAIL,
                message="Site does not use HTTPS — AI agents may deprioritise",
                score=0,
                weight=0.05,
            )
        )

    try:
        resp = await fetcher.get(base_url)
    except Exception:
        return results

    canonical = None
    if "text/html" in resp.headers.get("content-type", ""):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "lxml")
        link = soup.find("link", attrs={"rel": "canonical"})
        if link and link.get("href"):
            canonical = str(link["href"])

    if canonical:
        results.append(
            CheckResult(
                id="canonical_url",
                name="Canonical URL",
                category="Trust & Security",
                status=CheckStatus.PASS,
                message=f"Canonical: {canonical[:120]}",
                score=100,
                weight=0.03,
            )
        )
    else:
        results.append(
            CheckResult(
                id="canonical_url",
                name="Canonical URL",
                category="Trust & Security",
                status=CheckStatus.WARN,
                message="No canonical URL set — may confuse AI crawlers with duplicate content",
                score=40,
                weight=0.03,
            )
        )

    return results
