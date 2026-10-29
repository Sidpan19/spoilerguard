"""Input validation. Returns clear messages and never raises on bad user input."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .models import ONE_PIECE, VideoInput, ViewerProgress

MAX_FIELD_CHARS = {"title": 300, "description": 5000, "transcript": 5000}
SUPPORTED_SERIES = {ONE_PIECE}
MOCKED_SERIES_OK = True   # other series are accepted as free text and handled as mocked

NON_ENGLISH_WORDS = re.compile(
    r"\b(cap[ií]tulo|capitolo|reazione|reacci[oó]n|rea[cç][aã]o|kapitel|chapitre|episodio|"
    r"lettura|lectura|leitura|spoiler[s]? ita|sub ita)\b", re.I)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    post_date: Optional[date] = None
    progress: Optional[ViewerProgress] = None

    @property
    def ok(self) -> bool:
        return not self.errors


def _looks_non_english(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    non_ascii = sum(1 for c in letters if ord(c) > 127)
    return non_ascii / len(letters) > 0.3 or bool(NON_ENGLISH_WORDS.search(text))


def validate(video: VideoInput, raw_progress: dict[str, object]) -> ValidationResult:
    res = ValidationResult()

    if not (video.title or "").strip() and not (video.description or "").strip():
        res.errors.append("Title and description are both empty. Paste at least the video title.")

    lengths = {"title": video.title, "description": video.description,
               "transcript": video.transcript_excerpt}
    for name, text in lengths.items():
        if text and len(text) > MAX_FIELD_CHARS[name]:
            res.errors.append(f"{name.capitalize()} is {len(text)} characters; the limit is "
                              f"{MAX_FIELD_CHARS[name]}. Paste a shorter excerpt.")

    if not (video.post_date or "").strip():
        res.errors.append("Post date is missing. Use YYYY-MM-DD, as shown under the video.")
    else:
        try:
            res.post_date = date.fromisoformat(video.post_date.strip())
            if res.post_date > date.today():
                res.errors.append(f"Post date {res.post_date} is in the future.")
        except ValueError:
            res.errors.append(f"Post date '{video.post_date}' is not a valid date. Use YYYY-MM-DD.")

    progress: dict[str, object] = {}
    op = raw_progress.get(ONE_PIECE)
    if op is None or str(op).strip() == "":
        res.errors.append("One Piece progress is required: the last manga chapter you have read.")
    else:
        try:
            n = int(str(op).strip())
            if n < 0 or n > 3000:
                res.errors.append(f"One Piece progress {n} is out of range (0 to 3000).")
            progress[ONE_PIECE] = n
        except ValueError:
            res.errors.append(f"One Piece progress must be a chapter number, got '{op}'. "
                              "Anime episode progress is not supported yet.")
    for series, value in raw_progress.items():
        if series == ONE_PIECE or value is None or str(value).strip() == "":
            continue
        if series not in SUPPORTED_SERIES and not MOCKED_SERIES_OK:
            res.errors.append(f"Series '{series}' is not supported.")
        else:
            progress[series] = str(value).strip()
            res.warnings.append(f"'{series}' is not supported; its result is MOCKED (always RISKY).")
    res.progress = ViewerProgress(progress)

    if _looks_non_english(video.all_text()):
        res.warnings.append("Text may not be English. Rules are tuned for English; confidence is lowered.")
    return res
