"""Check robots.txt for AI bot accessibility."""

from __future__ import annotations

import re

from app.fetcher import Fetcher
from app.models import CheckResult, CheckStatus

AI_BOTS = [
    "GPTBot",
    "Google-Extended",
    "ChatGPT-User",
    "anthropic-ai",
    "ClaudeBot",
    "CCBot",
    "Bytespider",
    "PerplexityBot",
    "Applebot-Extended",
    "cohere-ai",
]

_BLANKET_DISALLOW = re.compile(r"^disallow:\s*/\s*$", re.MULTILINE)
_UA_LINE = re.compile(r"^user-agent:\s*", re.MULTILINE)


def _extract_section(text: str, start: int) -> str:
    """Return the robots.txt section starting at *start*, ending before the next User-agent line."""
    match = _UA_LINE.search(text, start + 1)
    end = match.start() if match else len(text)
    return text[start:end]


async def check_robots_txt(base_url: str, fetcher: Fetcher) -> list[CheckResult]:
    results: list[CheckResult] = []
    robots_url = f"{base_url}/robots.txt"

    try:
        resp = await fetcher.get(robots_url)
    except Exception:
        results.append(
            CheckResult(
                id="robots_exists",
                name="robots.txt exists",
                category="Agent Access",
                status=CheckStatus.FAIL,
                message="Could not fetch robots.txt",
                score=0,
                weight=0.08,
            )
        )
        return results

    if resp.status_code != 200:
        results.append(
            CheckResult(
                id="robots_exists",
                name="robots.txt exists",
                category="Agent Access",
                status=CheckStatus.FAIL,
                message=f"robots.txt returned HTTP {resp.status_code}",
                score=0,
                weight=0.08,
            )
        )
        return results

    text = resp.text.lower()
    results.append(
        CheckResult(
            id="robots_exists",
            name="robots.txt exists",
            category="Agent Access",
            status=CheckStatus.PASS,
            message="robots.txt is accessible",
            score=100,
            weight=0.08,
        )
    )

    blocked_bots: list[str] = []
    bots_with_sections: set[str] = set()
    for bot in AI_BOTS:
        ua_key = f"user-agent: {bot.lower()}"
        if ua_key in text:
            bots_with_sections.add(bot)
            section_start = text.index(ua_key)
            section = _extract_section(text, section_start)
            if _BLANKET_DISALLOW.search(section):
                blocked_bots.append(bot)

    if "user-agent: *" in text:
        star_idx = text.index("user-agent: *")
        star_section = _extract_section(text, star_idx)
        if _BLANKET_DISALLOW.search(star_section):
            blocked_bots.extend(
                bot for bot in AI_BOTS if bot not in blocked_bots and bot not in bots_with_sections
            )

    if blocked_bots:
        results.append(
            CheckResult(
                id="robots_ai_bots",
                name="AI bots not blocked",
                category="Agent Access",
                status=CheckStatus.FAIL,
                message=f"Blocked AI bots: {', '.join(blocked_bots)}",
                score=0,
                weight=0.10,
            )
        )
    else:
        results.append(
            CheckResult(
                id="robots_ai_bots",
                name="AI bots not blocked",
                category="Agent Access",
                status=CheckStatus.PASS,
                message="No AI bots explicitly blocked",
                score=100,
                weight=0.10,
            )
        )

    return results
