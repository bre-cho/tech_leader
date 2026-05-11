"""prompt_sanitizer — lightweight prompt injection guard for AI input fields.

Purpose
-------
User-controlled text that flows into LLM / video-generation prompts can carry
prompt-injection payloads designed to override system instructions or exfiltrate
data.  This module provides a validation + sanitisation layer that should be
applied to every user-supplied string before it is interpolated into a prompt.

Usage
-----
::

    from app.services.prompt_sanitizer import sanitize_prompt, PromptInjectionError

    clean = sanitize_prompt(user_text)          # raises on high-confidence injection
    clean = sanitize_prompt(user_text, raise_on_injection=False)  # strips, no raise

Patterns
--------
The guard detects common prompt-injection strategies:

* "Ignore (all) previous instructions"
* "You are now …" / "Act as …" role-swap attacks
* "Disregard (all) previous …"
* Delimiter injections (``[SYSTEM]``, ``<SYSTEM>``, ``###``)
* Nested instruction block markers (``[INST]``, ``<<SYS>>``)
* DAN / jailbreak trigger phrases
"""
from __future__ import annotations

import logging
import re
from typing import Sequence

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Detection patterns (ordered: most specific → most general)
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS: list[re.Pattern] = [
    # Direct override commands
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?previous\s+", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"override\s+(all\s+)?(previous\s+)?instructions?", re.IGNORECASE),
    # Role-swap / persona hijacking
    re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\b.*\bAI\b", re.IGNORECASE),
    re.compile(r"\bpretend\s+(you\s+are|to\s+be)\b", re.IGNORECASE),
    re.compile(r"\byour\s+new\s+(role|identity|persona|instructions?)\b", re.IGNORECASE),
    # Delimiter / system-block injections
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"<SYSTEM>", re.IGNORECASE),
    re.compile(r"<<SYS>>", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"###\s*system", re.IGNORECASE),
    # DAN / jailbreak trigger phrases
    re.compile(r"\bDAN\b"),
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),
]

# Compiled pattern for stripping detected segments (used in non-raise mode).
_STRIP_PATTERN = re.compile(
    "|".join(f"(?:{p.pattern})" for p in _INJECTION_PATTERNS),
    re.IGNORECASE,
)

# Maximum allowed prompt length (characters).  Prompts longer than this are
# truncated to prevent token-limit bypasses and excessive API costs.
_DEFAULT_MAX_LENGTH = 4_000


class PromptInjectionError(ValueError):
    """Raised when a high-confidence prompt injection attempt is detected.

    Attributes
    ----------
    matched_pattern:
        The regex pattern description that triggered the error.
    original_text:
        The input text (truncated to 200 chars in the message for safety).
    """

    def __init__(self, matched_pattern: str, original_text: str) -> None:
        self.matched_pattern = matched_pattern
        self.original_text = original_text
        preview = (original_text[:200] + "…") if len(original_text) > 200 else original_text
        super().__init__(
            f"Prompt injection detected (pattern={matched_pattern!r}): {preview!r}"
        )


def sanitize_prompt(
    text: str,
    *,
    max_length: int = _DEFAULT_MAX_LENGTH,
    raise_on_injection: bool = True,
    extra_patterns: Sequence[re.Pattern] | None = None,
    field_name: str = "prompt",
) -> str:
    """Validate and sanitise *text* before interpolating it into an AI prompt.

    Parameters
    ----------
    text:
        The user-supplied or untrusted string to check.
    max_length:
        Maximum character count.  Text is truncated at this limit after all
        other processing.  Default: 4 000 characters.
    raise_on_injection:
        When ``True`` (default) raise :class:`PromptInjectionError` on the
        first match.  When ``False`` silently strip the matched segments and
        log a WARNING instead.
    extra_patterns:
        Optional additional :class:`re.Pattern` objects to check beyond the
        built-in list.  Useful for application-specific forbidden phrases.
    field_name:
        Human-readable field label for log messages (e.g. ``"storyboard_prompt"``).

    Returns
    -------
    str
        Sanitised text, guaranteed to be ≤ *max_length* characters and free of
        detected injection payloads.

    Raises
    ------
    PromptInjectionError
        When *raise_on_injection* is ``True`` and an injection pattern is found.
    """
    if not isinstance(text, str):
        text = str(text or "")

    patterns = list(_INJECTION_PATTERNS)
    if extra_patterns:
        patterns = patterns + list(extra_patterns)

    for pattern in patterns:
        if pattern.search(text):
            _logger.warning(
                "prompt_sanitizer: injection pattern matched in field=%r pattern=%r text_preview=%r",
                field_name,
                pattern.pattern,
                text[:120],
            )
            if raise_on_injection:
                raise PromptInjectionError(matched_pattern=pattern.pattern, original_text=text)
            # Strip mode: remove the matched segment(s).
            text = _STRIP_PATTERN.sub("", text).strip()
            break  # re-evaluate after stripping; one pass is sufficient for known patterns

    # Enforce maximum length.
    if len(text) > max_length:
        _logger.warning(
            "prompt_sanitizer: truncating field=%r from %d to %d characters",
            field_name,
            len(text),
            max_length,
        )
        text = text[:max_length]

    return text


__all__ = ["sanitize_prompt", "PromptInjectionError"]
