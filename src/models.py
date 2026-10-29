"""Plain dataclasses shared by every layer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

ONE_PIECE = "One Piece"

FORMATS = (
    "live_reaction",   # live stream reacting to or reading a chapter
    "reaction",        # recorded reaction, including reactions to other creators
    "reading",         # chapter reading / walkthrough
    "discussion",      # weekly discussion, review, podcast
    "leak",            # pre-release spoilers, raw scans
    "theory",          # predictions, theories
    "ranking",         # tier list, power ranking, "strongest", ending the debate
    "versus",          # "X vs Y" debates
    "other",
)

# Formats that usually discuss whatever chapter is current when posted.
CURRENT_CHAPTER_FORMATS = {"live_reaction", "reaction", "reading", "discussion", "leak"}
# Formats that are risky even without any horizon signal.
RISKY_FORMATS = {"live_reaction", "reaction", "ranking", "versus", "theory", "leak", "discussion"}


@dataclass
class VideoInput:
    title: str
    description: str = ""
    channel: str = ""
    post_date: str = ""            # ISO yyyy-mm-dd
    transcript_excerpt: str = ""
    id: Optional[str] = None

    def fields(self) -> dict[str, str]:
        """Text fields scanned by the rules, keyed by source name."""
        return {
            "title": self.title or "",
            "description": self.description or "",
            "transcript": self.transcript_excerpt or "",
        }

    def all_text(self) -> str:
        return "\n".join(t for t in self.fields().values() if t)


@dataclass
class ViewerProgress:
    """series -> progress. One Piece is an int chapter; other series are free strings (mocked)."""
    progress: dict[str, object]

    @property
    def one_piece(self) -> Optional[int]:
        v = self.progress.get(ONE_PIECE)
        return v if isinstance(v, int) else None


@dataclass
class Evidence:
    source: str          # title, description, hashtag, transcript, timeline, entities, classifier
    quote: str
    detail: str = ""


@dataclass
class ChapterHit:
    chapter: int
    source: str
    quote: str


@dataclass
class EntityHit:
    entity: str
    first_chapter: int
    term: str
    source: str


@dataclass
class Classification:
    format: str = "other"
    temporal_cues: list[str] = field(default_factory=list)
    references_unreleased: bool = False
    source: str = "none"     # none, keyword, llm, cache
    notes: list[str] = field(default_factory=list)


@dataclass
class Signals:
    explicit_chapters: list[ChapterHit] = field(default_factory=list)
    hashtag_chapters: list[ChapterHit] = field(default_factory=list)
    episode_ambiguity: bool = False
    episode_quotes: list[str] = field(default_factory=list)
    warning_present: bool = False
    warning_quotes: list[str] = field(default_factory=list)
    leak_cue: bool = False
    classification: Classification = field(default_factory=Classification)
    latest_released: Optional[int] = None   # latest official chapter on or before post date
    date_cap: Optional[int] = None          # latest chapter that could have leaked by post date
    beyond_coverage: bool = False
    entity_hits: list[EntityHit] = field(default_factory=list)
    other_series: list[str] = field(default_factory=list)
    mentions_one_piece: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class SeriesVerdict:
    series: str
    verdict: str
    mocked: bool
    reason: str


@dataclass
class Decision:
    verdict: str                          # SAFE, RISKY, SPOILER
    horizon_low: Optional[int]
    horizon_high: Optional[int]
    confidence: str                       # high, medium, low
    rung: str
    evidence: list[Evidence] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    suggested_tag: str = ""
    unknown_defaulted_to_risky: bool = False
    other_series: list[SeriesVerdict] = field(default_factory=list)

    @property
    def estimated_horizon(self) -> Optional[int]:
        if self.horizon_low is not None and self.horizon_low == self.horizon_high:
            return self.horizon_low
        return None

    def horizon_text(self) -> str:
        lo, hi = self.horizon_low, self.horizon_high
        if lo is None and hi is None:
            return "unknown"
        if lo == hi:
            return f"Ch. {lo}"
        return f"Ch. {lo if lo is not None else '?'} to {hi if hi is not None else '?'}"
