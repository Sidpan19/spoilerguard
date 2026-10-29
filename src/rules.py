"""Deterministic regex layer: chapter numbers, episode ambiguity, warnings, entities, franchises."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import ChapterHit, EntityHit, Signals, VideoInput

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# "chapter 1196", "Manga Chapter 1196", "ch. 1196", "ch1196", "chap 1196"
CHAPTER_RE = re.compile(r"\b(?:chapter|chap\.?|ch\.?)\s*#?\s*(\d{1,4})\b", re.I)
# "#onepiece1132", "#OnePiece1195", "#onepiecechapter1196"
HASHTAG_RE = re.compile(r"#one\s*piece(?:chapter|ch)?(\d{3,4})\b", re.I)
# Bare number right after the series name: "ONE PIECE 1196", "One Piece manga 1196"
BARE_AFTER_NAME_RE = re.compile(r"(?<!#)\bone\s*piece\W{0,3}(?:manga\W{0,3})?(\d{4})\b", re.I)
# Episode wording means the number may be an anime episode, not a manga chapter.
EPISODE_RE = re.compile(r"\b(?:episode|ep\.?)\s*#?\s*(\d{1,4})\b|#one\s*piece\s*episode(\d{1,4})", re.I)
ANIME_RE = re.compile(r"\banime\b", re.I)

WARNING_RE = re.compile(r"\b(spoilers?|spoiler warning|leaks?|leaked|raw scans?|raws)\b", re.I)
LEAK_RE = re.compile(r"\b(leaks?|leaked|raw scans?|raws|confirmed spoilers?|first spoilers?|spoilers? summary|early spoilers?)\b", re.I)

ONE_PIECE_RE = re.compile(r"\b(one\s*piece|onepiece|luffy|straw\s*hats?)\b", re.I)
OTHER_SERIES = {
    "Naruto": r"\b(naruto|boruto|sasuke)\b",
    "Dragon Ball": r"\b(dragon\s*ball|goku|vegeta)\b",
    "Bleach": r"\b(bleach|ichigo)\b",
    "Jujutsu Kaisen": r"\b(jujutsu\s*kaisen|jjk|gojo|sukuna)\b",
    "My Hero Academia": r"\b(my\s*hero\s*academia|mha|deku)\b",
    "Demon Slayer": r"\b(demon\s*slayer|tanjiro)\b",
    "Hunter x Hunter": r"\b(hunter\s*x\s*hunter|hxh|gon\s+freecss)\b",
}

MAX_CHAPTER = 1999  # sanity bound; years like 2024 are never chapters


def _chapter_ok(n: int) -> bool:
    return 1 <= n <= MAX_CHAPTER


def find_chapters(video: VideoInput) -> tuple[list[ChapterHit], list[ChapterHit]]:
    """Return (explicit chapter hits, hashtag chapter hits) across all text fields."""
    explicit: list[ChapterHit] = []
    hashtags: list[ChapterHit] = []
    for source, text in video.fields().items():
        for m in HASHTAG_RE.finditer(text):
            n = int(m.group(1))
            if _chapter_ok(n):
                hashtags.append(ChapterHit(n, f"{source} hashtag", m.group(0)))
        for rx in (CHAPTER_RE, BARE_AFTER_NAME_RE):
            for m in rx.finditer(text):
                n = int(m.group(1))
                if _chapter_ok(n) and not any(h.chapter == n and h.source == source for h in explicit):
                    explicit.append(ChapterHit(n, source, m.group(0)))
    return explicit, hashtags


def find_episodes(video: VideoInput) -> list[str]:
    text = video.all_text()
    return [m.group(0) for m in EPISODE_RE.finditer(text)]


def load_entities(path: Path | None = None) -> list[dict]:
    path = path or DATA_DIR / "sample_entities.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        rows = [line for line in f if line.strip() and not line.lstrip().startswith("#")]
    out = []
    for r in csv.DictReader(rows):
        try:
            first = int(r["first_chapter"])
        except (KeyError, TypeError, ValueError):
            continue
        terms = [t.strip() for t in (r.get("match_terms") or r["entity"]).split("|") if t.strip()]
        out.append({"entity": r["entity"], "first_chapter": first, "terms": terms})
    return out


def find_entities(video: VideoInput, entities: list[dict]) -> list[EntityHit]:
    hits: list[EntityHit] = []
    for e in entities:
        for source, text in video.fields().items():
            found = None
            for term in e["terms"]:
                m = re.search(r"\b" + re.escape(term) + r"\b", text, re.I)
                if m:
                    found = m.group(0)
                    break
            if found:
                hits.append(EntityHit(e["entity"], e["first_chapter"], found, source))
                break  # one hit per entity is enough
    return hits


def extract(video: VideoInput, entities: list[dict] | None = None) -> Signals:
    """Run every regex rule and return the raw signals (no timeline, no classifier)."""
    s = Signals()
    text = video.all_text()

    explicit, hashtags = find_chapters(video)
    episodes = find_episodes(video)
    if episodes or ANIME_RE.search(text):
        s.episode_ambiguity = True
        s.episode_quotes = episodes or ["anime"]
        # Episode mapping is deferred: numbers in an episode/anime context are not manga chapters.
        ep_numbers = {int(re.sub(r"\D", "", q)) for q in episodes if re.search(r"\d", q)}
        explicit = [h for h in explicit if h.chapter not in ep_numbers or "chapter" in h.quote.lower()]
        hashtags = [h for h in hashtags if h.chapter not in ep_numbers]
        s.notes.append("Episode or anime wording found; episode to chapter mapping is deferred.")
    s.explicit_chapters = explicit
    s.hashtag_chapters = hashtags

    warnings = [m.group(0) for m in WARNING_RE.finditer(text)]
    s.warning_present = bool(warnings)
    s.warning_quotes = warnings
    s.leak_cue = bool(LEAK_RE.search(text))

    s.entity_hits = find_entities(video, load_entities() if entities is None else entities)
    s.mentions_one_piece = bool(ONE_PIECE_RE.search(text) or s.entity_hits or explicit or hashtags)
    s.other_series = [name for name, rx in OTHER_SERIES.items() if re.search(rx, text, re.I)]
    return s
