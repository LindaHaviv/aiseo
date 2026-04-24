"""AISEO — AI Agent SEO scoring API."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.fetcher import Fetcher, SSRFError
from app.fixes import generate_fixes
from app.models import CategoryScore, ScanRequest, ScanResponse, score_to_grade
from app.scanners.content import check_content
from app.scanners.headers import check_headers
from app.scanners.llms_txt import check_llms_txt
from app.scanners.meta_tags import check_meta_tags
from app.scanners.robots import check_robots_txt
from app.scanners.security import check_security
from app.scanners.sitemap import check_sitemap
from app.scanners.structured_data import check_structured_data

app = FastAPI(title="AISEO", version="0.1.0", description="AI Agent SEO scoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalise_url(raw: str) -> str:
    url = str(raw).strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/scan", response_model=ScanResponse)
async def scan(req: ScanRequest) -> ScanResponse:
    base_url = _normalise_url(str(req.url))
    fetcher = Fetcher()

    try:
        all_checks = []
        scanners = [
            check_robots_txt,
            check_llms_txt,
            check_sitemap,
            check_structured_data,
            check_meta_tags,
            check_content,
            check_headers,
            check_security,
        ]
        for scanner in scanners:
            try:
                results = await scanner(base_url, fetcher)
                all_checks.extend(results)
            except SSRFError:
                raise HTTPException(
                    status_code=400,
                    detail="URL targets a private or reserved address",
                )
            except Exception:
                continue

        if not all_checks:
            raise HTTPException(status_code=422, detail="Could not analyse the URL")

        # Build category scores
        categories_map: dict[str, list] = {}
        for check in all_checks:
            categories_map.setdefault(check.category, []).append(check)

        categories: list[CategoryScore] = []
        for name, checks in categories_map.items():
            total_weight = sum(c.weight for c in checks)
            if total_weight > 0:
                weighted_score = sum(c.score * c.weight for c in checks) / total_weight
            else:
                weighted_score = 0
            categories.append(
                CategoryScore(
                    name=name,
                    score=round(weighted_score, 1),
                    max_score=100,
                    checks=checks,
                )
            )

        # Overall score = weighted average across all checks
        total_weight = sum(c.weight for c in all_checks)
        if total_weight > 0:
            overall_score = sum(c.score * c.weight for c in all_checks) / total_weight
        else:
            overall_score = 0

        overall_score = round(min(max(overall_score, 0), 100), 1)
        fixes = generate_fixes(all_checks)

        return ScanResponse(
            url=base_url,
            score=overall_score,
            grade=score_to_grade(overall_score),
            categories=categories,
            fixes=fixes,
            scanned_at=datetime.now(timezone.utc).isoformat(),
        )
    finally:
        await fetcher.close()
