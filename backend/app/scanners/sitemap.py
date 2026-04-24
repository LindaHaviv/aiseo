"""Check sitemap.xml presence and quality."""

from __future__ import annotations

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_sitemap(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    for path in ["/sitemap.xml", "/sitemap_index.xml"]:
        url = f"{base_url}{path}"
        try:
            resp = await fetcher.get(url)
            if resp.status_code == 200 and ("<urlset" in resp.text or "<sitemapindex" in resp.text):
                loc_count = resp.text.lower().count("<loc>")
                results.append(
                    CheckResult(
                        id="sitemap_exists",
                        name="Sitemap present",
                        category="Discoverability",
                        status=CheckStatus.PASS,
                        message=f"Sitemap found at {path} with {loc_count} URLs",
                        score=100,
                        weight=0.06,
                    )
                )
                return results
        except Exception:
            continue

    results.append(
        CheckResult(
            id="sitemap_exists",
            name="Sitemap present",
            category="Discoverability",
            status=CheckStatus.FAIL,
            message="No sitemap.xml found",
            score=0,
            weight=0.06,
        )
    )
    return results
