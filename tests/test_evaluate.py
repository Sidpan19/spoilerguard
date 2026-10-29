import csv

from src import evaluate as E


def test_gold_label():
    assert E.gold_label(1132, 1050) == "spoiler"
    assert E.gold_label(1132, 1132) == "safe"


def test_all_rows_have_labels_and_stored_labels_agree():
    rows, skipped = E.load_golden()
    assert len(rows) == 10 and skipped == []
    for g in rows:
        for p, lab in g.stored.items():
            assert lab == E.gold_label(g.horizon, p), (g.video.id, p)


def test_tbd_rows_are_skipped(tmp_path):
    with open(E.GOLDEN, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows[1]["gold_horizon_chapter"] = "TBD"
    p = tmp_path / "g.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows[:2])
    kept, skipped = E.load_golden(p)
    assert len(kept) == 1 and skipped == [rows[1]["id"]]


def test_no_spoiler_is_missed_on_golden_set():
    rows, _ = E.load_golden()
    assert E.metrics(E.run_system(rows, "keyword"))["fn"] == 0


def test_shuffled_labels_drop_accuracy():
    rows, _ = E.load_golden()
    true_acc, shuffled = E.shuffle_check(rows, trials=10)
    assert shuffled < true_acc - 0.05


def test_warn_everything_baseline_flags_every_safe_case():
    rows, _ = E.load_golden()
    m = E.metrics(E.run_system(rows, None))
    assert m["tn"] == 0 and m["fn"] == 0
