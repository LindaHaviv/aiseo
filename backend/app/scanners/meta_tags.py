"""Check meta tags relevant to AI discoverability."""

from __future__ import annotations

from bs4 import BeautifulSoup

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_meta_tags(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        resp = await fetcher.get(base_url)
        if resp.status_code != 200:
            return results
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "lxml")

    title = soup.find("title")
    if title and title.string and len(title.string.strip()) > 5:
        results.append(
            CheckResult(
                id="meta_title",
                name="Page title",
                category="Content Clarity",
                status=CheckStatus.PASS,
                message=f'Title: "{title.string.strip()[:80]}"',
                score=100,
                weight=0.05,
            )
        )
    else:
        results.append(
            CheckResult(
                id="meta_title",
                name="Page title",
                category="Content Clarity",
                status=CheckStatus.FAIL,
                message="Missing or empty <title> tag",
                score=0,
                weight=0.05,
            )
        )

    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content") and len(str(desc["content"]).strip()) > 20:
        results.append(
            CheckResult(
                id="meta_description",
                name="Meta description",
                category="Content Clarity",
                status=CheckStatus.PASS,
                message=f"Description present ({len(str(desc['content']))} chars)",
                score=100,
                weight=0.05,
            )
        )
    else:
        results.append(
            CheckResult(
                id="meta_description",
                name="Meta description",
                category="Content Clarity",
                status=CheckStatus.FAIL,
                message="Missing or short meta description",
                score=0,
                weight=0.05,
            )
        )

    og_tags = soup.find_all("meta", attrs={"property": lambda v: v and v.startswith("og:")})
    if len(og_tags) >= 3:
        results.append(
            CheckResult(
                id="og_tags",
                name="Open Graph tags",
                category="Content Clarity",
                status=CheckStatus.PASS,
                message=f"{len(og_tags)} OG tags found",
                score=100,
                weight=0.04,
            )
        )
    else:
        results.append(
            CheckResult(
                id="og_tags",
                name="Open Graph tags",
                category="Content Clarity",
                status=CheckStatus.FAIL if not og_tags else CheckStatus.WARN,
                message=f"Only {len(og_tags)} OG tag(s) found (recommend >=3)",
                score=30 if og_tags else 0,
                weight=0.04,
            )
        )

    return results
