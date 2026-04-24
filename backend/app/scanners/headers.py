"""Check HTTP headers relevant to AI agent access."""

from __future__ import annotations

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_headers(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    try:
        resp = await fetcher.get(base_url)
    except Exception:
        return results

    x_robots = resp.headers.get("x-robots-tag", "").lower()
    if "noindex" in x_robots or "nofollow" in x_robots:
        results.append(
            CheckResult(
                id="x_robots_tag",
                name="X-Robots-Tag header",
                category="Agent Access",
                status=CheckStatus.FAIL,
                message=f"X-Robots-Tag blocks indexing: {x_robots}",
                score=0,
                weight=0.06,
            )
        )
    else:
        results.append(
            CheckResult(
                id="x_robots_tag",
                name="X-Robots-Tag header",
                category="Agent Access",
                status=CheckStatus.PASS,
                message="No restrictive X-Robots-Tag header",
                score=100,
                weight=0.06,
            )
        )

    if resp.status_code == 200:
        results.append(
            CheckResult(
                id="http_status",
                name="HTTP status",
                category="Agent Access",
                status=CheckStatus.PASS,
                message="Page returns HTTP 200",
                score=100,
                weight=0.03,
            )
        )
    else:
        results.append(
            CheckResult(
                id="http_status",
                name="HTTP status",
                category="Agent Access",
                status=CheckStatus.FAIL,
                message=f"Page returns HTTP {resp.status_code}",
                score=0,
                weight=0.03,
            )
        )

    ct = resp.headers.get("content-type", "")
    if "text/html" in ct:
        results.append(
            CheckResult(
                id="content_type",
                name="Content-Type header",
                category="Agent Access",
                status=CheckStatus.PASS,
                message="Serves text/html",
                score=100,
                weight=0.02,
            )
        )
    else:
        results.append(
            CheckResult(
                id="content_type",
                name="Content-Type header",
                category="Agent Access",
                status=CheckStatus.WARN,
                message=f"Content-Type: {ct or 'missing'}",
                score=50,
                weight=0.02,
            )
        )

    return results
