"""Evaluate the checker on the golden set.

python -m src.evaluate            # writes docs/eval_results.md and docs/eval_results.csv

Eval input is the title plus the hashtags recorded in the CSV (no description text was
collected). Gold label at viewer progress P: spoiler if gold_horizon_chapter > P, else safe.
"""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path

from .decide import check
from .models import ONE_PIECE, VideoInput

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "data" / "golden_set.csv"
CATCH_UP = [100, 400, 900, 1100, 1150]
CURRENT = [1190, 1195, 1196]
PROFILES = CATCH_UP + CURRENT
SYSTEMS = {
    "a_rules_only": "none",
    "b_rules_keyword": "keyword",
    "c_rules_llm_cache": "llm",
    "d_warn_everything": None,
}


@dataclass
class GoldRow:
    video: VideoInput
    group: str
    horizon: int
    stored: dict[int, str]   # labels stored in the CSV for 1100/1190/1196


def load_golden(path: Path = GOLDEN) -> tuple[list[GoldRow], list[str]]:
    rows, skipped = [], []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                h = int(r["gold_horizon_chapter"].strip())
            except (ValueError, AttributeError):
                skipped.append(r["id"])
                continue
            v = VideoInput(id=r["id"], title=r["title"], description=r.get("hashtags", ""),
                           channel=r["channel"], post_date=r["date"])
            stored = {p: r.get(f"label_viewer_ch{p}", "") for p in (1100, 1190, 1196)}
            rows.append(GoldRow(v, r["group"], h, stored))
    return rows, skipped


def gold_label(horizon: int, progress: int) -> str:
    return "spoiler" if horizon > progress else "safe"


def run_system(rows: list[GoldRow], mode: str | None, horizons: list[int] | None = None) -> list[dict]:
    """One record per (row, profile). horizons overrides gold horizons (used by the shuffle test)."""
    out = []
    for i, g in enumerate(rows):
        h = horizons[i] if horizons else g.horizon
        for p in PROFILES:
            if mode is None:
                verdict, rung, reason, tag, horizon_text, cls = "RISKY", "baseline", "Warns on every video.", "", "", "none"
            else:
                _, d, s = check(g.video, {ONE_PIECE: p}, mode=mode, allow_api=False)
                verdict, rung, reason = d.verdict, d.rung, d.reasons[0]
                tag, horizon_text, cls = d.suggested_tag, d.horizon_text(), s.classification.source
            out.append({"id": g.video.id, "group": g.group, "progress": p, "gold_horizon": h,
                        "gold": gold_label(h, p), "verdict": verdict,
                        "warn": verdict in ("SPOILER", "RISKY"), "rung": rung, "reason": reason,
                        "horizon": horizon_text, "tag": tag, "classifier": cls})
    return out


def metrics(records: list[dict]) -> dict:
    tp = sum(r["warn"] and r["gold"] == "spoiler" for r in records)
    fn = sum(not r["warn"] and r["gold"] == "spoiler" for r in records)
    fp = sum(r["warn"] and r["gold"] == "safe" for r in records)
    tn = sum(not r["warn"] and r["gold"] == "safe" for r in records)
    decisive = [r for r in records if r["verdict"] in ("SAFE", "SPOILER")]
    decisive_ok = sum((r["verdict"] == "SPOILER") == (r["gold"] == "spoiler") for r in decisive)
    return {"n": len(records), "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": (tp, tp + fn), "false_alarm": (fp, fp + tn), "precision": (tp, tp + fp),
            "accuracy": (tp + tn, len(records)), "decisive": (len(decisive), len(records)),
            "decisive_correct": (decisive_ok, len(decisive))}


def accuracy(records: list[dict]) -> float:
    m = metrics(records)
    return m["accuracy"][0] / m["accuracy"][1] if m["accuracy"][1] else 0.0


def _fmt(pair: tuple[int, int]) -> str:
    a, b = pair
    return f"{a}/{b}" + (f" ({100 * a / b:.0f}%)" if b else "")


def shuffle_check(rows: list[GoldRow], seed: int = 7, trials: int = 20) -> tuple[float, float]:
    """Accuracy of the keyword system with true vs shuffled gold horizons."""
    true_acc = accuracy(run_system(rows, "keyword"))
    rng = random.Random(seed)
    accs = []
    for _ in range(trials):
        hs = [g.horizon for g in rows]
        rng.shuffle(hs)
        accs.append(accuracy(run_system(rows, "keyword", hs)))
    return true_acc, sum(accs) / len(accs)


def main() -> None:
    rows, skipped = load_golden()
    results = {name: run_system(rows, mode) for name, mode in SYSTEMS.items()}

    lines = ["# Evaluation results", "",
             f"Golden set rows used: {len(rows)}. Skipped for missing gold labels: {len(skipped)}"
             + (f" ({', '.join(skipped)})" if skipped else "") + ".",
             f"Viewer profiles: catching up {CATCH_UP}, current {CURRENT}. "
             f"{len(rows)} videos x {len(PROFILES)} profiles = {len(rows) * len(PROFILES)} cases per system.",
             "Input per video: title + hashtags recorded in the CSV. No description text.",
             "'Warn' means verdict SPOILER or RISKY. n is tiny; read counts, not percentages.", ""]

    lines += ["## Overall", "",
              "| System | Recall (spoilers warned) | False alarms (safe warned) | Precision | Accuracy | Decisive (SAFE/SPOILER) | Decisive correct |",
              "|---|---|---|---|---|---|---|"]
    for name, recs in results.items():
        m = metrics(recs)
        lines.append(f"| {name} | {_fmt(m['recall'])} | {_fmt(m['false_alarm'])} | {_fmt(m['precision'])} | "
                     f"{_fmt(m['accuracy'])} | {_fmt(m['decisive'])} | {_fmt(m['decisive_correct'])} |")

    for title, pick in [("By group", lambda r, k: r["group"] == k), ("By viewer type", None)]:
        lines += ["", f"## {title}", "",
                  "| System | Slice | Recall | False alarms | Accuracy | Decisive |", "|---|---|---|---|---|---|"]
        slices = ([("explicit (E)", lambda r: r["group"] == "explicit"), ("weak (W)", lambda r: r["group"] == "weak")]
                  if pick else
                  [("catching up", lambda r: r["progress"] in CATCH_UP), ("current", lambda r: r["progress"] in CURRENT)])
        for name, recs in results.items():
            for label, f in slices:
                m = metrics([r for r in recs if f(r)])
                lines.append(f"| {name} | {label} | {_fmt(m['recall'])} | {_fmt(m['false_alarm'])} | "
                             f"{_fmt(m['accuracy'])} | {_fmt(m['decisive'])} |")

    # Per-video verdict grid for the LLM system
    grid = results["c_rules_llm_cache"]
    lines += ["", "## Verdicts per video (system c)", "",
              "Cell = verdict / gold. Wrong hard verdicts in bold.", "",
              "| id | gold H | horizon found | " + " | ".join(str(p) for p in PROFILES) + " |",
              "|---|---|---|" + "---|" * len(PROFILES)]
    for g in rows:
        rs = [r for r in grid if r["id"] == g.video.id]
        cells = []
        for r in rs:
            cell = f"{r['verdict']} / {r['gold']}"
            wrong_hard = (r["verdict"] == "SAFE" and r["gold"] == "spoiler") or (r["verdict"] == "SPOILER" and r["gold"] == "safe")
            cells.append(f"**{cell}**" if wrong_hard else cell)
        lines.append(f"| {g.video.id} | {g.horizon} | {rs[0]['horizon']} | " + " | ".join(cells) + " |")

    # Failure analysis
    lines += ["", "## Failure analysis (systems b and c)", "",
              "Misses (spoiler not warned) are the costly error. False alarms are RISKY or SPOILER on a safe case.", ""]
    for name in ("b_rules_keyword", "c_rules_llm_cache"):
        fails = [r for r in results[name] if r["warn"] != (r["gold"] == "spoiler")]
        lines.append(f"**{name}**: {len(fails)} errors "
                     f"({sum(not r['warn'] for r in fails)} misses, {sum(r['warn'] for r in fails)} false alarms)")
        lines.append("")
        for r in fails:
            kind = "MISS" if not r["warn"] else "FALSE ALARM"
            lines.append(f"- {kind} {r['id']} at Ch. {r['progress']}: verdict {r['verdict']}, horizon found "
                         f"{r['horizon']}, gold {r['gold_horizon']}. Rung: {r['rung']}. {r['reason']}")
        lines.append("")

    # Consistency + sanity
    mismatches = [f"{g.video.id}@{p}" for g in rows for p, lab in g.stored.items()
                  if lab and lab != gold_label(g.horizon, p)]
    true_acc, shuf_acc = shuffle_check(rows)
    cached = sum(r["classifier"] == "cache" for r in results["c_rules_llm_cache"]) // len(PROFILES)
    lines += ["## Checks", "",
              f"- Stored CSV labels vs labels computed from gold horizon: "
              f"{'all match' if not mismatches else 'MISMATCH ' + ', '.join(mismatches)}.",
              f"- Shuffle sanity (system b): accuracy {true_acc:.2f} with true horizons vs "
              f"{shuf_acc:.2f} mean over 20 shuffles. A working eval should drop.",
              f"- System c used cached LLM output for {cached}/{len(rows)} videos; the rest fell back to keywords.",
              ""]

    out = ROOT / "docs" / "eval_results.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    with open(ROOT / "docs" / "eval_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["system"] + list(next(iter(results.values()))[0].keys()))
        w.writeheader()
        for name, recs in results.items():
            for r in recs:
                w.writerow({"system": name, **r})
    print("\n".join(lines))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
