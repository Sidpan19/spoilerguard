"""Suggested creator tag. Depends on the video only, not on the viewer."""
from __future__ import annotations

from typing import Optional

from .models import RISKY_FORMATS, Signals


def suggest_tag(lo: Optional[int], hi: Optional[int], lo_rung: str, s: Signals) -> str:
    if lo is not None and lo == hi and lo_rung.startswith(("1", "2")):
        tag = f"Manga spoilers up to Ch. {lo}"
    elif lo_rung.startswith("3"):
        tag = f"Discusses current chapters (up to Ch. {hi})"
    elif lo is None and s.classification.format not in RISKY_FORMATS and not s.entity_hits:
        tag = "No chapter-specific content detected"
    else:
        tag = "Horizon unclear: add a progress label"
    if s.warning_present:
        tag += " (text already warns about spoilers)"
    return tag
