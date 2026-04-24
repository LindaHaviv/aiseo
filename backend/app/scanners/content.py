"""Analyse page content clarity and semantic HTML usage."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus

SEMANTIC_TAGS = {"article", "section", "nav", "aside", "header", "footer", "main", "figure"}


async def check_content(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        resp = await fetcher.get(base_url)
        if resp.status_code != 200:
            return results
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    body = soup.find("body")
    if not body:
        return results

    text = body.get_text(separator=" ", strip=True)
    html_len = len(resp.text)
    text_len = len(text)
    ratio = (text_len / html_len * 100) if html_len > 0 else 0

    if ratio >= 15:
        score = 100
        status = CheckStatus.PASS
        msg = f"Text-to-HTML ratio: {ratio:.1f}% (good)"
    elif ratio >= 8:
        score = 60
        status = CheckStatus.WARN
        msg = f"Text-to-HTML ratio: {ratio:.1f}% (could be higher)"
    else:
        score = 20
        status = CheckStatus.FAIL
        msg = f"Text-to-HTML ratio: {ratio:.1f}% (low — AI agents may struggle)"

    results.append(
        CheckResult(
            id="text_html_ratio",
            name="Text-to-HTML ratio",
            category="Content Clarity",
            status=status,
            message=msg,
            score=score,
            weight=0.05,
        )
    )

    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    if len(headings) >= 2:
        results.append(
            CheckResult(
                id="heading_structure",
                name="Heading structure",
                category="Content Clarity",
                status=CheckStatus.PASS,
                message=f"{len(headings)} headings found",
                score=100,
                weight=0.04,
            )
        )
    else:
        results.append(
            CheckResult(
                id="heading_structure",
                name="Heading structure",
                category="Content Clarity",
                status=CheckStatus.FAIL,
                message="Fewer than 2 headings — page lacks structure for AI parsing",
                score=20,
                weight=0.04,
            )
        )

    found_semantic = {tag.name for tag in soup.find_all(SEMANTIC_TAGS)}
    semantic_count = len(found_semantic)
    if semantic_count >= 3:
        score = 100
        status = CheckStatus.PASS
    elif semantic_count >= 1:
        score = 50
        status = CheckStatus.WARN
    else:
        score = 0
        status = CheckStatus.FAIL

    results.append(
        CheckResult(
            id="semantic_html",
            name="Semantic HTML",
            category="Content Clarity",
            status=status,
            message=f"Semantic tags: {', '.join(sorted(found_semantic)) or 'none'}",
            score=score,
            weight=0.05,
        )
    )

    return results
