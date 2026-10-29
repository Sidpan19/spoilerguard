"""Combine signals into a horizon range and a verdict for one viewer.

The horizon is a range [low, high]:
  - low  comes from content: explicit chapter, leak cue, temporal cue, named entity.
  - high comes from the post date: a video cannot discuss a chapter not out (or leaking) yet.
Verdict for viewer progress P:  low > P -> SPOILER,  high <= P -> SAFE,  otherwise RISKY.
"""
from __future__ import annotations

from typing import Optional

from . import classify as classify_mod
from . import rules, timeline
from .models import (CURRENT_CHAPTER_FORMATS, ONE_PIECE, RISKY_FORMATS, Decision, Evidence,
                     SeriesVerdict, Signals, VideoInput)
from .tags import suggest_tag
from .validate import ValidationResult, validate

LOWER = {"high": "medium", "medium": "low", "low": "low"}


def gather_signals(video: VideoInput, post_date, mode: str = "keyword", refresh_cache: bool = False,
                   allow_api: bool = True, entities: list[dict] | None = None,
                   table: list | None = None) -> Signals:
    s = rules.extract(video, entities)
    s.classification = classify_mod.classify(video, mode=mode, refresh_cache=refresh_cache,
                                             allow_api=allow_api)
    b = timeline.bounds_for(post_date, table)
    s.latest_released, s.date_cap, s.beyond_coverage = b.latest_released, b.date_cap, b.beyond_coverage
    s.notes.append(b.note)
    return s


def bounds(s: Signals) -> tuple[Optional[int], Optional[int], str, str, str, list[Evidence], list[str]]:
    """Return (low, high, low_rung, high_rung, low_confidence, evidence, reasons)."""
    lo: Optional[int] = None
    hi: Optional[int] = None
    lo_rung = hi_rung = ""
    lo_conf = "low"
    ev: list[Evidence] = []
    why: list[str] = []
    c = s.classification

    # Rung 1: explicit chapter number. Hashtag-only numbers are weaker (could be an episode).
    if s.explicit_chapters:
        top = max(s.explicit_chapters, key=lambda h: h.chapter)
        lo = hi = top.chapter
        lo_rung = hi_rung = "1 explicit chapter"
        lo_conf = "high"
        for h in s.explicit_chapters:
            ev.append(Evidence(h.source, h.quote, f"Ch. {h.chapter}"))
        why.append(f"Explicit chapter number: Ch. {top.chapter}.")
    elif s.hashtag_chapters:
        top = max(s.hashtag_chapters, key=lambda h: h.chapter)
        lo = hi = top.chapter
        lo_rung = hi_rung = "1 explicit chapter (hashtag only)"
        lo_conf = "medium"
        for h in s.hashtag_chapters:
            ev.append(Evidence(h.source, h.quote, f"Ch. {h.chapter}"))
        why.append(f"Only a hashtag gives a number (Ch. {top.chapter}); it could mean an anime episode.")

    # Rung 2: spoiler or leak wording.
    if s.warning_present:
        ev.append(Evidence("text", ", ".join(dict.fromkeys(s.warning_quotes)), "spoiler/leak wording"))
        why.append("The text already warns about spoilers (lowers harm, not the horizon).")
    if lo is None and (s.leak_cue or c.references_unreleased) and s.latest_released is not None:
        lo = hi = s.latest_released + 1
        lo_rung = hi_rung = "2 leak wording + date"
        lo_conf = "medium"
        why.append(f"Leak wording with no number: assumes the next unreleased chapter, Ch. {lo}.")

    # Rung 3: current-chapter format + temporal cue -> at least the latest official chapter.
    if (lo is None and c.format in CURRENT_CHAPTER_FORMATS and c.temporal_cues
            and s.latest_released is not None):
        lo = s.latest_released
        lo_rung = "3 date + temporal cue"
        lo_conf = "medium"
        ev.append(Evidence("classifier", ", ".join(c.temporal_cues), f"format {c.format}"))
        why.append(f"{c.format} with recency cues, posted when Ch. {s.latest_released} was latest.")

    # Rung 4: named entities raise the lower bound.
    if s.entity_hits:
        top = max(s.entity_hits, key=lambda e: e.first_chapter)
        for e in s.entity_hits:
            ev.append(Evidence(e.source, e.term, f"{e.entity}: first in Ch. {e.first_chapter}"))
        if lo is None or top.first_chapter > lo:
            if lo is not None and lo == hi:
                why.append(f"Names {top.entity} (Ch. {top.first_chapter}), later than the stated chapter; kept the stated chapter.")
            else:
                lo = top.first_chapter
                lo_rung = "4 named entity"
                lo_conf = "medium"
                why.append(f"Names {top.entity}, who first appears in Ch. {top.first_chapter}: horizon is at least that.")

    # Date cap: upper bound from the release table.
    if hi is None and s.date_cap is not None:
        hi = s.date_cap
        hi_rung = "date cap"
        ev.append(Evidence("timeline", f"latest Ch. {s.latest_released}, cap Ch. {s.date_cap}",
                           "beyond table coverage" if s.beyond_coverage else "release table + leak window"))
        why.append(f"Posted when at most Ch. {s.date_cap} could be out or leaking.")
    if lo is not None and hi is not None and lo > hi:
        why.append(f"Content points past the date cap (Ch. {lo} > Ch. {hi}); trusting the content.")
        hi = lo
    return lo, hi, lo_rung, hi_rung, lo_conf, ev, why


def decide(s: Signals, progress: int, warnings: list[str] | None = None,
           other_progress: dict[str, str] | None = None) -> Decision:
    lo, hi, lo_rung, hi_rung, lo_conf, ev, why = bounds(s)
    fmt = s.classification.format

    if lo is not None and lo > progress:
        verdict, rung, conf = "SPOILER", lo_rung, lo_conf
        why.insert(0, f"Horizon is at least Ch. {lo}, past your Ch. {progress}.")
    elif hi is not None and hi <= progress:
        verdict, rung = "SAFE", hi_rung
        conf = "high" if hi_rung.startswith("1 explicit chapter") and "hashtag" not in hi_rung else "medium"
        why.insert(0, f"Horizon is at most Ch. {hi}, within your Ch. {progress}.")
    else:
        verdict, conf = "RISKY", "low"
        rung = "5 format risk" if fmt in RISKY_FORMATS else "6 unknown, defaulted to risky"
        if lo is None and hi is None:
            why.insert(0, "No horizon signal found. Unknowns default to RISKY.")
        else:
            why.insert(0, f"Horizon ({_range(lo, hi)}) overlaps your Ch. {progress}; cannot rule a spoiler in or out.")
        if fmt in RISKY_FORMATS:
            why.append(f"Format '{fmt}' often covers recent chapters.")

    if s.episode_ambiguity:
        conf = "medium" if conf == "high" else conf
        why.append("Mentions an episode or the anime; episode mapping is deferred.")
    if warnings and any("English" in w for w in warnings):
        conf = LOWER[conf]
    if not s.mentions_one_piece:
        why.append("No One Piece reference found in the text.")

    others = []
    seen = set()
    for series in list(s.other_series) + list((other_progress or {}).keys()):
        if series in seen or series == ONE_PIECE:
            continue
        seen.add(series)
        given = (other_progress or {}).get(series)
        others.append(SeriesVerdict(series, "RISKY", True,
                                    f"MOCKED: no rules or release data for {series}"
                                    + (f" (your progress: {given})" if given else "") + "."))
    if others:
        why.append("Video touches another franchise: " + ", ".join(o.series for o in others) + " (mocked).")

    d = Decision(verdict=verdict, horizon_low=lo, horizon_high=hi, confidence=conf, rung=rung,
                 evidence=ev, reasons=why, unknown_defaulted_to_risky=verdict == "RISKY",
                 other_series=others)
    d.suggested_tag = suggest_tag(lo, hi, lo_rung, s)
    return d


def _range(lo, hi) -> str:
    return f"Ch. {lo if lo is not None else '?'} to {hi if hi is not None else '?'}"


def check(video: VideoInput, raw_progress: dict[str, object], mode: str = "llm",
          refresh_cache: bool = False, allow_api: bool = True
          ) -> tuple[ValidationResult, Optional[Decision], Optional[Signals]]:
    """Full pipeline. Returns (validation, decision or None, signals or None)."""
    v = validate(video, raw_progress)
    if not v.ok:
        return v, None, None
    s = gather_signals(video, v.post_date, mode=mode, refresh_cache=refresh_cache, allow_api=allow_api)
    other = {k: str(val) for k, val in v.progress.progress.items() if k != ONE_PIECE}
    d = decide(s, v.progress.one_piece, v.warnings, other)
    return v, d, s
