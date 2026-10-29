from src import rules


def chapters(v):
    explicit, tags = rules.find_chapters(v)
    return sorted({h.chapter for h in explicit}), sorted({h.chapter for h in tags})


def test_e1_chapter_word(video):
    assert chapters(video("YAPPPING One Piece Chapter 1196 w/ Tier 3 (short)")) == ([1196], [])


def test_e2_manga_chapter_live(video):
    assert chapters(video("One Piece Manga Chapter 1196 LIVE Reaction")) == ([1196], [])


def test_e3_bare_number_after_series_name_and_hashtag(video):
    assert chapters(video("ONE PIECE 1196 BLIND READING REACTION", "#onepiece1196")) == ([1196], [1196])


def test_e4_chapter_first(video):
    assert chapters(video("Chapter 1196 [One Piece] - MelonTeee")) == ([1196], [])


def test_e5_leak_and_warning(video):
    s = rules.extract(video("ONE PIECE CHAPTER 1195 - FIRST CONFIRMED SPOILER", "#OnePiece1195"), [])
    assert [h.chapter for h in s.explicit_chapters] == [1195]
    assert s.warning_present and s.leak_cue


def test_w1_hashtag_only_is_not_explicit(video):
    s = rules.extract(video("ENDING THE DEBATE: Top 30 Strongest One Piece Characters!", "#onepiece1132"), [])
    assert s.explicit_chapters == []
    assert [h.chapter for h in s.hashtag_chapters] == [1132]


def test_short_forms(video):
    assert chapters(video("One Piece ch. 1190 thoughts"))[0] == [1190]
    assert chapters(video("op ch1190 review"))[0] == [1190]


def test_no_number_cases(video):
    for t in ["King Of Lightning Reacts To Shanks VS Mihawk Is Simple!",
              "So Naruto vs Luffy is Happening...",
              "Top 30 Strongest One Piece Characters!"]:
        assert chapters(video(t)) == ([], [])


def test_years_are_not_chapters(video):
    assert chapters(video("One Piece 2026 recap"))[0] == []


def test_episode_ambiguity(video):
    s = rules.extract(video("One Piece Episode 1122 reaction"), [])
    assert s.episode_ambiguity
    assert s.explicit_chapters == [] and s.hashtag_chapters == []


def test_episode_does_not_remove_explicit_chapter(video):
    s = rules.extract(video("One Piece Episode 1122 vs Chapter 1196"), [])
    assert s.episode_ambiguity
    assert [h.chapter for h in s.explicit_chapters] == [1196]


def test_blind_is_not_a_safety_signal(video):
    s = rules.extract(video("ONE PIECE 1196 BLIND READING REACTION"), [])
    assert [h.chapter for h in s.explicit_chapters] == [1196]


ENTS = [{"entity": "Blackbeard", "first_chapter": 223, "terms": ["Blackbeard"]},
        {"entity": "Shamrock", "first_chapter": 1134, "terms": ["Shamrock", "Figarland"]}]


def test_entity_hits_with_possessive(video):
    s = rules.extract(video("Blackbeard's WEAKEST LINK Might Be His SECRET Weapon!"), ENTS)
    assert [(e.entity, e.first_chapter) for e in s.entity_hits] == [("Blackbeard", 223)]


def test_entity_word_boundary(video):
    assert rules.extract(video("Shamrocks and clovers"), ENTS).entity_hits == []


def test_entities_table_loads_and_empty_is_ok(tmp_path):
    assert any(e["entity"] == "Blackbeard" for e in rules.load_entities())
    p = tmp_path / "e.csv"
    p.write_text("# empty\nentity,first_chapter,match_terms,source_note\n", encoding="utf-8")
    assert rules.load_entities(p) == []
    assert rules.load_entities(tmp_path / "missing.csv") == []


def test_other_franchise(video):
    s = rules.extract(video("So Naruto vs Luffy is Happening..."), [])
    assert s.other_series == ["Naruto"] and s.mentions_one_piece
