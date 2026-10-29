from datetime import date

from src import timeline

T = [(1194, date(2026, 9, 27)), (1195, date(2026, 10, 11)), (1196, date(2026, 10, 18))]


def test_table_loads_in_order():
    t = timeline.load_timeline()
    assert t[0][0] == 1100 and t[-1] == (1196, date(2026, 10, 18))
    assert all(b[0] == a[0] + 1 and b[1] > a[1] for a, b in zip(t, t[1:]))


def test_leak_window_reaches_next_chapter():
    b = timeline.bounds_for(date(2026, 10, 6), T)   # E5: posted 5 days before 1195
    assert b.latest_released == 1194 and b.date_cap == 1195 and not b.beyond_coverage


def test_reaction_before_official_release():
    b = timeline.bounds_for(date(2026, 10, 16), T)  # E2: 2 days before 1196
    assert b.latest_released == 1195 and b.date_cap == 1196 and not b.beyond_coverage


def test_beyond_coverage():
    b = timeline.bounds_for(date(2026, 10, 25), T)
    assert b.latest_released == 1196 and b.date_cap == 1197 and b.beyond_coverage


def test_before_table_and_empty_table():
    assert timeline.bounds_for(date(2020, 1, 1), T).date_cap is None
    assert timeline.bounds_for(date(2026, 10, 1), []).date_cap is None


def test_w4_2024_date_with_real_table():
    b = timeline.bounds_for(date(2024, 8, 19))
    assert b.latest_released == 1123 and b.date_cap == 1124
