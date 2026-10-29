from src.models import VideoInput
from src.validate import validate


def test_valid():
    r = validate(VideoInput(title="One Piece Chapter 1196", post_date="2026-10-16"), {"One Piece": "1100"})
    assert r.ok and r.progress.one_piece == 1100 and not r.warnings


def test_empty_title_and_description():
    r = validate(VideoInput(title=" ", description="", post_date="2026-10-16"), {"One Piece": 1100})
    assert not r.ok and "empty" in r.errors[0]


def test_bad_missing_and_future_date():
    assert "not a valid date" in validate(VideoInput(title="x", post_date="16/10/2026"), {"One Piece": 1}).errors[0]
    assert "missing" in validate(VideoInput(title="x"), {"One Piece": 1}).errors[0]
    assert "future" in validate(VideoInput(title="x", post_date="2099-01-01"), {"One Piece": 1}).errors[0]


def test_progress_must_be_int():
    r = validate(VideoInput(title="x", post_date="2026-10-16"), {"One Piece": "episode 1100"})
    assert not r.ok and "chapter number" in r.errors[0]
    assert not validate(VideoInput(title="x", post_date="2026-10-16"), {}).ok


def test_too_long():
    r = validate(VideoInput(title="x" * 301, post_date="2026-10-16"), {"One Piece": 1})
    assert not r.ok and "limit" in r.errors[0]


def test_other_series_is_mocked_warning():
    r = validate(VideoInput(title="x", post_date="2026-10-16"), {"One Piece": 1, "Naruto": "ep 200"})
    assert r.ok and r.progress.progress["Naruto"] == "ep 200" and "MOCKED" in r.warnings[0]


def test_non_english_warns_but_runs():
    r = validate(VideoInput(title="One Piece capitolo 1196 reazione", post_date="2026-10-16"), {"One Piece": 1})
    assert r.ok and "English" in r.warnings[0]
