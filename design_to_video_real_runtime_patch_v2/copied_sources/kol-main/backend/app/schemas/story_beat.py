from __future__ import annotations

from enum import Enum


class BeatType(str, Enum):
    hook = "hook"
    setup = "setup"
    escalation = "escalation"
    conflict = "conflict"
    reveal = "reveal"
    climax = "climax"
    resolution = "resolution"
    cta = "cta"
    callback = "callback"
