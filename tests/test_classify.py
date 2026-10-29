import json

from src import classify as C
from src.models import VideoInput


def v(title, desc="", date="2026-10-16"):
    return VideoInput(title=title, description=desc, post_date=date)


def test_keyword_formats():
    cases = {
        "One Piece Manga Chapter 1196 LIVE Reaction": "live_reaction",
        "ONE PIECE CHAPTER 1195 - FIRST CONFIRMED SPOILER": "leak",
        "ONE PIECE 1196 BLIND READING REACTION": "reading",
        "King Of Lightning Reacts To Shanks VS Mihawk Is Simple!": "reaction",
        "ENDING THE DEBATE: Top 30 Strongest One Piece Characters!": "ranking",
        "So Naruto vs Luffy is Happening...": "versus",
        "YAPPPING One Piece Chapter 1196 w/ Tier 3 (short)": "discussion",
        "Cooking pasta": "other",
    }
    for title, fmt in cases.items():
        assert C.keyword_classify(v(title)).format == fmt, title


def test_keyword_cues_are_exact_substrings():
    c = C.keyword_classify(v("We JUST read the new chapter"))
    assert c.temporal_cues == ["JUST", "new chapter"]


def test_validate_drops_invented_cues_and_rejects_bad_schema():
    ok, notes = C._validate({"format": "reaction", "temporal_cues": ["latest", "chapter 1197"],
                             "references_unreleased": False}, "the latest reaction")
    assert ok.temporal_cues == ["latest"] and notes
    bad, _ = C._validate({"format": "plot summary", "temporal_cues": [], "references_unreleased": False}, "x")
    assert bad is None
    bad, _ = C._validate(["not", "a", "dict"], "x")
    assert bad is None


def test_cache_is_used_without_api(tmp_path, monkeypatch):
    video = v("Some title")
    path = tmp_path / "cache.json"
    path.write_text(json.dumps({C.cache_key(video): {"model": "m", "result": {
        "format": "theory", "temporal_cues": [], "references_unreleased": False}}}), encoding="utf-8")

    def no_api(*a, **k):
        raise AssertionError("API called")
    monkeypatch.setattr(C, "llm_classify", no_api)
    c = C.classify(video, mode="llm", cache_path=path)
    assert c.source == "cache" and c.format == "theory"


def test_no_key_falls_back_to_keywords(tmp_path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    c = C.classify(v("Luffy reaction"), mode="llm", cache_path=tmp_path / "none.json")
    assert c.source == "keyword" and "fallback" in c.notes[-1]


def test_api_error_falls_back_and_is_not_cached(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")

    def boom(*a, **k):
        raise RuntimeError("429 rate limited")
    monkeypatch.setattr(C, "llm_classify", boom)
    c = C.classify(v("Luffy reaction"), mode="llm", cache_path=tmp_path / "c.json")
    assert c.source == "keyword" and "429" in c.notes[-1]
    assert not (tmp_path / "c.json").exists()


def test_cache_key_changes_with_date():
    assert C.cache_key(v("a", date="2026-01-01")) != C.cache_key(v("a", date="2026-01-02"))


def test_golden_cache_complete():
    from src.evaluate import load_golden
    cache = C.load_cache()
    rows, _ = load_golden()
    assert all(C.cache_key(g.video) in cache for g in rows)
