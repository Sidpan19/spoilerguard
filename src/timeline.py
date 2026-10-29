"""Release table lookup. Turns a post date into chapter bounds."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Scans and spoilers circulate before the official date. Observed in the golden set:
# E5 posted 5 days before ch. 1195, E2/E3 2 days before ch. 1196, E1 1 day before.
# 7 days rounds that up so the cap errs toward warning.
LEAK_WINDOW_DAYS = 7


@dataclass
class Bounds:
    latest_released: Optional[int]  # latest official chapter on or before the post date
    date_cap: Optional[int]         # latest chapter that could have leaked by the post date
    beyond_coverage: bool           # post date is past the end of the table
    note: str


def load_timeline(path: Path | None = None) -> list[tuple[int, date]]:
    path = path or DATA_DIR / "sample_timeline.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        rows = [line for line in f if line.strip() and not line.lstrip().startswith("#")]
    table = []
    for r in csv.DictReader(rows):
        try:
            table.append((int(r["chapter"]), date.fromisoformat(r["release_date"].strip())))
        except (KeyError, ValueError):
            continue
    return sorted(table)


def _latest_on_or_before(table: list[tuple[int, date]], d: date) -> Optional[int]:
    latest = None
    for ch, rel in table:
        if rel <= d:
            latest = ch
        else:
            break
    return latest


def bounds_for(post_date: date, table: list[tuple[int, date]] | None = None,
               leak_window_days: int = LEAK_WINDOW_DAYS) -> Bounds:
    table = load_timeline() if table is None else table
    if not table:
        return Bounds(None, None, False, "Timeline table is empty; no date bounds.")
    first_ch, first_date = table[0]
    last_ch, last_date = table[-1]
    if post_date < first_date:
        return Bounds(None, None, False,
                      f"Post date is before the timeline starts (Ch. {first_ch}, {first_date}); no date bounds.")
    latest = _latest_on_or_before(table, post_date)
    leak_horizon = post_date + timedelta(days=leak_window_days)
    # Assumption: at most one chapter per week, so the chapter after the table's last row
    # cannot be officially out before last_date + 7 days.
    if leak_horizon >= last_date + timedelta(days=7):
        # Past the table: the next chapter may already be out or leaking, and we cannot know.
        cap = last_ch + 1
        return Bounds(latest, cap, True,
                      f"Post date is near or past the end of the timeline (Ch. {last_ch}, {last_date}); "
                      f"cap set to Ch. {cap}, beyond coverage.")
    cap = _latest_on_or_before(table, leak_horizon)
    return Bounds(latest, cap, False,
                  f"Latest official chapter by {post_date}: Ch. {latest}. "
                  f"With a {leak_window_days}-day leak window, nothing past Ch. {cap} can be discussed.")
