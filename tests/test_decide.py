from datetime import date

from src import rules
from src.decide import check, decide
from src.models import Classification, VideoInput
from src.timeline import bounds_for

T = [(1123, date(2024, 8, 18)), (1124, date(2024, 8, 25)),
     (1194, date(2026, 9, 27)), (1195, date(2026, 10, 11)), (1196, date(2026, 10, 18))]
ENTS = [{"entity": "Blackbeard", "first_chapter": 223, "terms": ["Blackbeard"]},
        {"entity": "Mihawk", "first_chapter": 49, "terms": ["Mihawk"]}]


def signals(title, d, fmt="other", cues=(), desc=""):
    s = rules.extract(VideoInput(title=title, description=desc, post_date=d), ENTS)
    s.classification = Classification(format=fmt, temporal_cues=list(cues), source="test")
    b = bounds_for(date.fromisoformat(d), T)
    s.latest_released, s.date_cap, s.beyond_coverage = b.latest_released, b.date_cap, b.beyond_coverage
    return s


def test_explicit_spoiler_and_safe():
    s = signals("One Piece Manga Chapter 1196 LIVE Reaction", "2026-10-16", "live_reaction")
    d = decide(s, 1100)
    assert (d.verdict, d.estimated_horizon, d.confidence) == ("SPOILER", 1196, "high")
    assert d.rung.startswith("1")
    assert decide(s, 1196).verdict == "SAFE"


def test_catch_up_reader_spoiled_by_old_hashtag():
    s = signals("Top 30 Strongest One Piece Characters!", "2024-11-30", "ranking", desc="#onepiece1132")
    assert decide(s, 1050).verdict == "SPOILER"
    assert decide(s, 1050).confidence == "medium"
    assert decide(s, 1150).verdict == "SAFE"


def test_entity_lower_bound_and_date_cap():
    s = signals("Blackbeard's WEAKEST LINK Might Be His SECRET Weapon!", "2024-08-19", "theory")
    assert decide(s, 100).verdict == "SPOILER"          # Blackbeard first appears in 223
    assert decide(s, 900).verdict == "RISKY"            # 223..1124 overlaps 900
    d = decide(s, 1196)
    assert d.verdict == "SAFE" and d.rung == "date cap"  # a 2024 video cannot reach 1196


def test_weekly_reader_one_behind_is_warned():
    s = signals("So Naruto vs Luffy is Happening...", "2026-10-25", "versus")
    d = decide(s, 1195)
    assert d.verdict == "RISKY" and d.unknown_defaulted_to_risky
    assert [o.series for o in d.other_series] == ["Naruto"] and d.other_series[0].mocked


def test_unknown_never_silently_safe():
    s = signals("Some video", "2026-10-25")
    s.date_cap = s.latest_released = None
    d = decide(s, 1196)
    assert d.verdict == "RISKY" and d.horizon_low is None and d.horizon_high is None
    assert d.rung.startswith("6")


def test_leak_wording_without_number_points_at_next_chapter():
    s = signals("One Piece leaks are crazy", "2026-10-06", "leak")
    d = decide(s, 1194)
    assert d.verdict == "SPOILER" and d.estimated_horizon == 1195
    assert decide(s, 1195).verdict == "SAFE"


def test_temporal_cue_with_current_format():
    s = signals("Reacting to the new chapter!", "2026-10-16", "reaction", cues=["new chapter"])
    d = decide(s, 1190)
    assert d.verdict == "SPOILER" and d.horizon_low == 1195 and d.horizon_high == 1196
    assert decide(s, 1195).verdict == "RISKY"
    assert "Discusses current chapters" in d.suggested_tag


def test_temporal_cue_ignored_for_non_current_format():
    s = signals("Mihawk is finally explained", "2026-10-16", "theory", cues=["finally"])
    assert decide(s, 1100).verdict == "RISKY"


def test_tags():
    s = signals("ONE PIECE CHAPTER 1195 - FIRST CONFIRMED SPOILER", "2026-10-06", "leak")
    assert decide(s, 1100).suggested_tag == "Manga spoilers up to Ch. 1195 (text already warns about spoilers)"
    s = signals("Cooking with friends", "2026-10-06", "other")
    assert decide(s, 1196).suggested_tag == "No chapter-specific content detected"
    s = signals("So Naruto vs Luffy is Happening...", "2026-10-25", "versus")
    assert decide(s, 1196).suggested_tag == "Horizon unclear: add a progress label"


def test_tag_does_not_depend_on_viewer():
    s = signals("One Piece Chapter 1196 discussion", "2026-10-17", "discussion")
    assert decide(s, 100).suggested_tag == decide(s, 1196).suggested_tag


def test_check_invalid_returns_no_decision():
    v, d, s = check(VideoInput(title="", description="", post_date="16/10/2026"), {"One Piece": "abc"},
                    mode="keyword")
    assert not v.ok and d is None and len(v.errors) == 3


def test_check_mocked_second_series():
    v, d, s = check(VideoInput(title="So Naruto vs Luffy is Happening...", post_date="2026-10-25"),
                    {"One Piece": 1195, "Naruto": "Shippuden ep 200"}, mode="keyword")
    assert d.verdict == "RISKY"
    assert d.other_series[0].series == "Naruto" and "Shippuden ep 200" in d.other_series[0].reason
