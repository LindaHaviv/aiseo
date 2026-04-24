"""Unit tests for models."""

from __future__ import annotations

from app.models import Grade, score_to_grade


def test_score_to_grade():
    assert score_to_grade(95) == Grade.A
    assert score_to_grade(90) == Grade.A
    assert score_to_grade(80) == Grade.B
    assert score_to_grade(75) == Grade.B
    assert score_to_grade(65) == Grade.C
    assert score_to_grade(60) == Grade.C
    assert score_to_grade(50) == Grade.D
    assert score_to_grade(40) == Grade.D
    assert score_to_grade(30) == Grade.F
    assert score_to_grade(0) == Grade.F
