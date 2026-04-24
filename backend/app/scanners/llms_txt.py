"""Check for llms.txt and llms-full.txt presence."""

from __future__ import annotations

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus


async def check_llms_txt(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []

    for filename, check_id, weight in [
        ("llms.txt", "llms_txt", 0.08),
        ("llms-full.txt", "llms_full_txt", 0.04),
    ]:
        url = f"{base_url}/{filename}"
        try:
            resp = await fetcher.get(url)
            if resp.status_code == 200 and len(resp.text.strip()) > 20:
                results.append(
                    CheckResult(
                        id=check_id,
                        name=f"{filename} present",
                        category="Agent Access",
                        status=CheckStatus.PASS,
                        message=f"{filename} found ({len(resp.text)} chars)",
                        score=100,
                        weight=weight,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        id=check_id,
                        name=f"{filename} present",
                        category="Agent Access",
                        status=CheckStatus.FAIL,
                        message=f"{filename} not found or empty",
                        score=0,
                        weight=weight,
                    )
                )
        except Exception:
            results.append(
                CheckResult(
                    id=check_id,
                    name=f"{filename} present",
                    category="Agent Access",
                    status=CheckStatus.FAIL,
                    message=f"Could not fetch {filename}",
                    score=0,
                    weight=weight,
                )
            )

    return results
