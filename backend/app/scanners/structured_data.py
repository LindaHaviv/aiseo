"""Check for JSON-LD / Schema.org structured data."""

from __future__ import annotations

import json

from bs4 import BeautifulSoup

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_structured_data(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        resp = await fetcher.get(base_url)
        if resp.status_code != 200:
            results.append(
                CheckResult(
                    id="structured_data",
                    name="Structured data (JSON-LD)",
                    category="Structured Data",
                    status=CheckStatus.SKIP,
                    message=f"Page returned HTTP {resp.status_code}",
                    score=0,
                    weight=0.08,
                )
            )
            return results
    except Exception:
        results.append(
            CheckResult(
                id="structured_data",
                name="Structured data (JSON-LD)",
                category="Structured Data",
                status=CheckStatus.SKIP,
                message="Could not fetch page",
                score=0,
                weight=0.08,
            )
        )
        return results

    soup = BeautifulSoup(resp.text, "lxml")
    ld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})

    if not ld_scripts:
        results.append(
            CheckResult(
                id="structured_data",
                name="Structured data (JSON-LD)",
                category="Structured Data",
                status=CheckStatus.FAIL,
                message="No JSON-LD structured data found",
                score=0,
                weight=0.08,
            )
        )
        return results

    types_found: list[str] = []
    for script in ld_scripts:
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                t = data.get("@type", "Unknown")
                types_found.append(t if isinstance(t, str) else str(t))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        t = item.get("@type", "Unknown")
                        types_found.append(t if isinstance(t, str) else str(t))
        except (json.JSONDecodeError, TypeError):
            continue

    results.append(
        CheckResult(
            id="structured_data",
            name="Structured data (JSON-LD)",
            category="Structured Data",
            status=CheckStatus.PASS,
            message=f"Found {len(ld_scripts)} JSON-LD block(s): {', '.join(types_found[:5])}",
            score=100,
            weight=0.08,
        )
    )
    return results
