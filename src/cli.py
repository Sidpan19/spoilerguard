"""Command line entry.

python -m src.cli --title "One Piece Chapter 1196 LIVE Reaction" --date 2026-10-16 --progress 1100
python -m src.cli --golden E2 --progress 1100
python -m src.cli --build-cache            # classify every golden video with Groq and cache it
Flags: --no-llm (keyword classifier only), --refresh-cache (ignore cache, call the API).
"""
from __future__ import annotations

import argparse
import sys
import time

from .classify import classify
from .decide import check
from .evaluate import load_golden
from .models import ONE_PIECE, VideoInput


def print_result(video: VideoInput, progress: dict, mode: str, refresh: bool) -> int:
    v, d, s = check(video, progress, mode=mode, refresh_cache=refresh)
    for w in v.warnings:
        print(f"WARNING: {w}")
    if not v.ok:
        for e in v.errors:
            print(f"INVALID INPUT: {e}")
        return 2
    print(f"Verdict:    {d.verdict}  (confidence {d.confidence})")
    print(f"Horizon:    {d.horizon_text()}")
    print(f"Rung:       {d.rung}")
    print(f"Classifier: {s.classification.source}, format {s.classification.format}, "
          f"cues {s.classification.temporal_cues}")
    print("Reasons:")
    for r in d.reasons:
        print(f"  - {r}")
    print("Evidence:")
    for e in d.evidence:
        print(f"  - [{e.source}] \"{e.quote}\" {e.detail}")
    for o in d.other_series:
        print(f"Other series: {o.series}: {o.verdict} ({o.reason})")
    print(f"Suggested creator tag: {d.suggested_tag}")
    return 0


def build_cache(refresh: bool) -> None:
    rows, skipped = load_golden()
    for g in rows:
        c = classify(g.video, mode="llm", refresh_cache=refresh)
        print(f"{g.video.id}: {c.source:8} format={c.format:14} cues={c.temporal_cues} "
              f"unreleased={c.references_unreleased} {'; '.join(c.notes)}")
        if c.source == "llm":
            time.sleep(2)  # stay well under free-tier rate limits
    if skipped:
        print(f"Skipped (no gold label): {skipped}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Spoiler-risk checker for One Piece YouTube metadata.")
    p.add_argument("--title", default="")
    p.add_argument("--description", default="")
    p.add_argument("--channel", default="")
    p.add_argument("--date", default="", help="post date, YYYY-MM-DD")
    p.add_argument("--transcript", default="")
    p.add_argument("--progress", default="", help="last One Piece manga chapter read")
    p.add_argument("--other-series", nargs=2, metavar=("SERIES", "PROGRESS"),
                   help="second series progress (mocked)")
    p.add_argument("--golden", help="run a golden-set video by id, e.g. E2")
    p.add_argument("--no-llm", action="store_true", help="keyword classifier only")
    p.add_argument("--refresh-cache", action="store_true", help="ignore the cache and call the API")
    p.add_argument("--build-cache", action="store_true", help="classify all golden videos via the LLM")
    a = p.parse_args(argv)

    if a.build_cache:
        build_cache(a.refresh_cache)
        return 0
    if a.golden:
        rows, _ = load_golden()
        match = [g for g in rows if g.video.id == a.golden.upper()]
        if not match:
            print(f"No golden video with id {a.golden}")
            return 2
        video = match[0].video
    else:
        video = VideoInput(title=a.title, description=a.description, channel=a.channel,
                           post_date=a.date, transcript_excerpt=a.transcript)
    progress: dict[str, object] = {ONE_PIECE: a.progress}
    if a.other_series:
        progress[a.other_series[0]] = a.other_series[1]
    return print_result(video, progress, "keyword" if a.no_llm else "llm", a.refresh_cache)


if __name__ == "__main__":
    sys.exit(main())
