"""Input validation, length limits, and prompt-injection heuristics."""

from __future__ import annotations

import re
from dataclasses import dataclass

from config.settings import Settings, get_settings

_INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+",
    r"disregard\s+the\s+above",
    r"<\s*script",
)


@dataclass
class GuardResult:
    ok: bool
    message: str | None = None
    trimmed: str | None = None
    possible_injection: bool = False
    moderation_flagged: bool = False


def heuristic_injection(text: str) -> bool:
    lower = text.lower()
    for pat in _INJECTION_PATTERNS:
        if re.search(pat, lower, re.IGNORECASE):
            return True
    return False


def validate_message(text: str, settings: Settings | None = None) -> GuardResult:
    s = settings or get_settings()
    if len(text) > s.max_message_chars:
        return GuardResult(
            ok=False,
            message=f"Message too long (max {s.max_message_chars} characters).",
        )
    inj = heuristic_injection(text)
    return GuardResult(ok=True, trimmed=text, possible_injection=inj)


async def moderate_openai_if_enabled(text: str, settings: Settings | None = None) -> GuardResult:
    """Optional OpenAI moderation; returns ok=False if flagged."""
    s = settings or get_settings()
    base = validate_message(text, s)
    if not base.ok:
        return base

    if not s.enable_openai_moderation or not s.openai_api_key:
        return base

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=s.openai_api_key)
        res = await client.moderations.create(input=text)
        flagged = res.results[0].flagged if res.results else False
        if flagged:
            return GuardResult(
                ok=False,
                message="Your message could not be processed due to content policy.",
                moderation_flagged=True,
                possible_injection=base.possible_injection,
            )
    except Exception:
        # Fail open for availability unless you prefer fail-closed
        pass

    return base
