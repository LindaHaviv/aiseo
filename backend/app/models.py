"""Pydantic models for AISEO scan requests and responses."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ScanRequest(BaseModel):
    url: HttpUrl


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


class CheckResult(BaseModel):
    id: str
    name: str
    category: str
    status: CheckStatus
    message: str
    score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)


class Fix(BaseModel):
    id: str
    check_id: str
    title: str
    description: str
    priority: Literal["critical", "high", "medium", "low"]
    effort: Literal["easy", "medium", "hard"]
    score_lift: float = Field(ge=0, description="Estimated score-point improvement")
    code_snippet: str | None = None


class CategoryScore(BaseModel):
    name: str
    score: float
    max_score: float
    checks: list[CheckResult]


class ScanResponse(BaseModel):
    url: str
    score: float = Field(ge=0, le=100)
    grade: Grade
    categories: list[CategoryScore]
    fixes: list[Fix]
    scanned_at: str


def score_to_grade(score: float) -> Grade:
    if score >= 90:
        return Grade.A
    if score >= 75:
        return Grade.B
    if score >= 60:
        return Grade.C
    if score >= 40:
        return Grade.D
    return Grade.F
