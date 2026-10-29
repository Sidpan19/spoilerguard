# CLAUDE.md: Spoiler-Risk Checker (MiraFlores AI case study)

This file is the full context and implementation plan. Read it completely before writing code. The golden set is in `golden_set_seed.csv` in this folder.

## 0. Working rules for Claude Code

- Hard time box: the whole case study is 2 to 4 hours. Build in the order of section 8. If behind schedule, cut from the stretch list in section 9, never from evaluation or README.
- Keep `docs/TIME_LOG.md` and `docs/AI_USAGE.md` updated as you go (what was generated, what was checked and how). The submission requires both.
- Never invent data. You cannot know recent One Piece chapters, release dates or first appearances. Every table in `data/` must be user-supplied or marked `SAMPLE, user-verified` in the file header. If a value is missing, leave it blank and say so.
- Do not scrape YouTube. Input is pasted metadata only.
- Label everything honestly in the UI and README as implemented, mocked or deferred.
- Python 3.11+, minimal dependencies. Prefer plain functions and dataclasses over frameworks. Add tests for every rule.
- No secrets in the repo. The LLM is Groq (free tier); the key comes from `GROQ_API_KEY` (locally) or Streamlit secrets (deployed). Model via `GROQ_MODEL`, default `openai/gpt-oss-120b`. The app must also run with no key by using cached LLM outputs (section 6).
- Style for any prose written for the user: direct, brief, no em dashes.

## 1. Context

The candidate (Siddhesh Pande) is applying for the "AI Engineer (Tax)" role at MiraFlores AI. The first stage is an open-topic case study:

1. Describe 3 problems from personal experience, choose one, and separate what is observed from what is assumed.
2. Explain how people handle it today, the smallest first step, one rejected alternative, and what would make him decide the problem is not worth solving.
3. Build a live prototype that completes one core workflow from realistic input to meaningful output, plus a demo of one difficult or invalid-input case. Synthetic data and mocked integrations are allowed if labeled.
4. Submit: write-up (max 4 pages), prototype link, source code, README (setup, dependencies, sample data, example inputs and outputs), time spent, what he would investigate next, how AI was used and how it was checked, and what is implemented, mocked or deferred. A 5 to 10 minute video walkthrough is also required.
5. After submission there is a 15-minute prototype run, then a separate 30-minute live case. The prototype must be explainable line by line by the candidate.

What the reviewers value: problem framing, honest separation of observed vs assumed, judgment about scope, evaluation, and candour about limits. A small, correct, well-evaluated tool beats a broad, flashy one.

## 2. The chosen problem

Anime and manga fans get spoiled by YouTube videos. Titles, thumbnails, descriptions and AI summaries leak plot, and the viewer cannot tell from the surface whether a video is safe for their reading or watching progress.

Problem statement: given a video's metadata and the viewer's progress in a series, estimate whether the video is likely to contain spoilers beyond that progress, explain the evidence, and suggest how the creator could label it.

### Observed (from the candidate's own experience and the 10 collected videos)
- Explicit leaks exist: titles with chapter numbers and live reaction or reading streams (group E in the CSV).
- "Blind reaction" usually describes the creator, not the viewer. A blind reaction to chapter 1196 is still a spoiler for someone at chapter 1100.
- Leak and spoiler-prediction videos point past the latest official release (E5 posts a "confirmed spoiler" for chapter 1195 before release).
- Spoilers also appear in descriptions and in platform-generated summaries that restate plot.
- Reaction videos have a hidden input (the linked original video), so the title alone may understate the horizon.
- Many results are non-English.
- Weak-signal videos exist: no chapter number, vague temporal words, empty descriptions, hashtags that carry the only signal (group W).

### Assumed (not verified, say so in the write-up)
- Fans want a per-series progress setting rather than a global spoiler filter.
- Creators would adopt a suggested horizon tag if it were easy.
- The 10-video sample reflects the wider distribution (it does not; it is a hand-built seed, not a random sample).
- Chapter vs anime episode confusion is common (observed anecdotally, not measured).

### How people handle it today
Muting keywords, avoiding YouTube and social media after a release, relying on creator-added spoiler warnings, watching only creators they trust, and spoiler-tag conventions on forums. These are manual, coarse, and fail on weak-signal videos.

### Smallest first step
This prototype: a layered checker over pasted metadata for one franchise (One Piece manga chapters), evaluated on a hand-labeled set.

### Rejected alternative
A pure "ask an LLM whether this is a spoiler" approach. Rejected because an LLM cannot know recent chapters, will hallucinate horizons, and cannot be audited. The design uses rules and user-supplied tables first and uses the LLM only for classification of format and cues, never for recalling plot.

### What would make me stop (kill criterion)
If, in a larger sample of videos, most already label their horizon clearly (chapter number or explicit warning in title or description), the unlabeled remainder is too small to justify a tool. Also stop if the weak-signal group cannot be separated from safe videos better than a "warn on every reaction or live video" baseline.

## 3. Scope

In scope (implemented):
- One Piece manga chapters, English metadata, pasted by the user.
- Input: title, description, channel, post date, optional transcript excerpt, viewer progress per series.
- Rule layer, format and cue classification, timeline check, decision, evidence, suggested creator tag.
- Evaluation over the golden set at three viewer profiles (ch. 1100, 1190, 1196).
- Streamlit UI plus CLI, hosted at a live link.

Mocked (must be labeled): second franchise handling for W5 (progress entered as a string, rules mocked), LLM responses cached for the sample videos so graders can run without a key.

Deferred (list in README): scraping or YouTube API, following linked original videos (W2), non-English, anime episode to manga chapter mapping, live chat and comments, thumbnails and OCR, creator-side plugin, accuracy beyond the sample.

## 4. Data

Files in `data/`:

- `golden_set.csv`: copy of `golden_set_seed.csv`. Columns: id, group, title, channel, subscribers, date, date_type, views, language, horizon_signal, horizon_source, format, temporal_cues, spoiler_warning_in_text, platform_summary_shown, notes, gold_horizon_chapter, label_viewer_ch1100, label_viewer_ch1190, label_viewer_ch1196.
  - Group E (E1 to E5): explicit. Gold labels are filled. E1 to E4 horizon 1196, E5 horizon 1195 (pre-release leak).
  - Group W (W1 to W5): weak signal. W1 labels come from the hashtag `#onepiece1132` and are marked unverified. W2 to W5 gold fields are TBD and must be filled by the candidate before the final evaluation run. The eval script must skip rows with TBD labels and print how many were skipped.
  - Label semantics: `spoiler` if the video's true horizon chapter is greater than the viewer's progress, else `safe`.
- `sample_timeline.csv`: columns `chapter, release_date, source_note`. SAMPLE DATA. The candidate fills this from a public source (for example the series' official release listing). Needs at least the chapters around the golden-set dates (about 1090 to 1196). Do not fill from memory. Header comment: `# SAMPLE DATA, user-verified`.
- `sample_entities.csv`: columns `entity, first_chapter, source_note`. SAMPLE DATA, a small hand-built list (10 to 20 entries) used to raise the horizon lower bound when a video names a character or event. Leave empty until the candidate supplies it; code must work when it is empty.
- `llm_cache.json`: cached classifier outputs keyed by video id (section 6).

Rows must never contain real viewer data. Video metadata is the candidate's pasted text.

## 5. Architecture

```
spoilerguard/
  CLAUDE.md
  README.md
  requirements.txt
  data/            (files above)
  docs/            TIME_LOG.md, AI_USAGE.md, WRITEUP.md, VIDEO_SCRIPT.md
  src/
    models.py      dataclasses: VideoInput, ViewerProgress, Signals, Decision
    validate.py    input validation and error messages
    rules.py       regex layer
    timeline.py    release table lookup, horizon estimation from date
    classify.py    format and cue classification (LLM + keyword fallback + cache)
    decide.py      combine signals into a decision
    tags.py        suggested creator tag
    evaluate.py    metrics over golden set
    cli.py         command line entry
  app.py           Streamlit UI
  tests/
```

### Data model
- `VideoInput`: id (optional), title, description, channel, post_date (ISO), transcript_excerpt (optional).
- `ViewerProgress`: dict series -> progress. One Piece: manga chapter integer. Others: free string (mocked).
- `Signals`: explicit_chapters (list of ints with source and quote), hashtag_chapters, warning_present (bool), format (enum), temporal_cues (list), date_estimate (chapter or None), entity_hits (list), notes.
- `Decision`: verdict (SAFE, RISKY, SPOILER), estimated_horizon (int or None), confidence (high, medium, low), rung (which signal ladder step decided), evidence (quoted snippets), reasons (short strings), suggested_tag, unknown_defaulted_to_risky (bool).

## 6. Layers and logic

Signal ladder, strongest first. The first rung that yields a horizon decides; lower rungs only add evidence or raise confidence.

1. **Explicit chapter number** (rules.py). Patterns in title, hashtags, description: `chapter 1196`, `ch. 1196`, `ch1196`, `#onepiece1132`, bare 4-digit numbers near the series name. Handle chapter vs episode: if the text says "episode" or "ep", flag `episode_ambiguity` and do not treat as a manga chapter (mapping is deferred, so verdict is RISKY with a note). Confidence high.
2. **Spoiler-warning text**. Words like "spoilers", "leak", "raw scans", "confirmed spoiler" combined with a chapter number means horizon equals that chapter (leaks point at the unreleased chapter). A warning in text lowers the harm but not the horizon; record `warning_present` so the tag suggestion can say the video is already labeled.
3. **Date vs timeline** (timeline.py). If the format is reaction, reading, discussion or live and temporal cues are present ("just", "latest", "this week", "new chapter"), take the most recent chapter released on or before the post date as the estimated horizon. Medium confidence. For leak formats before a release, horizon is the next chapter after the latest released.
4. **Entity hits** (sample_entities.csv). If the video names an entity with `first_chapter` N, horizon >= N. Low to medium confidence. Skip if the table is empty.
5. **Format risk default**. Reaction, live, tier list, power ranking, versus, theory, "ending the debate" style videos with no horizon: RISKY, low confidence.
6. **Unknown**. No signals: horizon None, verdict RISKY, `unknown_defaulted_to_risky = true`. Never silently SAFE.

### Decision per viewer progress P and horizon H
- H known and H <= P: SAFE.
- H known and H > P: SPOILER.
- H unknown: RISKY (all unknowns default to risky; recall is prioritized over precision).
- Multi-series: evaluate each series the video could touch. If the text names two franchises (W5), run One Piece logic for One Piece and return RISKY/mocked for the other series with a clear label.

### classify.py (LLM layer)
- Model call classifies only: format (enum above), temporal cues (list of exact substrings from the text), whether the video appears to reference unreleased material. It must never state plot or chapter content from memory.
- Use the Groq API (JSON mode) with output validated by a schema. Reject and retry once on invalid JSON, then fall back to the keyword classifier.
- Keyword fallback: deterministic regex and keyword lists per format. This is also the "rules only" baseline in evaluation.
- Cache: `data/llm_cache.json` keyed by sha256 of (title + description + date). If the cache has the key, use it and never call the API. Add `--no-llm` and `--refresh-cache` flags. The deployed demo uses the cache for sample videos and the live API only if a key is present for pasted new input.
- Prompt-injection note: video text is untrusted. Put it inside delimiters, instruct the model to treat it as data, and validate output against the schema. Document this in the write-up.

### tags.py
Return a suggested creator tag from the decision: "Manga spoilers up to Ch. N", "Discusses current chapters (up to Ch. N)", "No chapter-specific content detected", or "Horizon unclear: add a progress label". If a warning is already present, say so.

### validate.py (invalid-input case)
Reject with clear messages, never crash: empty title and description, unparseable date, unsupported series, progress not an integer for One Piece, text over a length limit, non-English detected (warn, still run with low confidence). The demo must show one of these.

## 7. Evaluation

`python -m src.evaluate` produces a table and writes `docs/eval_results.md`.

- Rows: golden-set videos with filled labels. Profiles: viewer at ch. 1100, 1190, 1196. A prediction counts as "warn" if verdict is SPOILER or RISKY.
- Metrics: spoiler recall (primary), false alarm rate on gold-safe cases, precision, accuracy. Report overall and per group (E vs W).
- Systems compared: (a) rules only, (b) rules plus keyword classifier, (c) rules plus LLM classifier (cache), (d) trivial baseline "warn on every video".
- Report how many rows were skipped for TBD labels. Do not report numbers as if they generalize: n is about 10, so give counts, not percentages alone.
- Expected honest result: group E near perfect, group W worse. Include a failure analysis section listing each missed or false-alarm case and why (for example W5 two franchises and empty description, W2 hidden linked original).
- Add a short sanity test that shuffling the labels drops accuracy (guards against a broken eval).

## 8. Build order and time budget (4 hours max)

| Time | Task |
|---|---|
| 0:00 to 0:20 | Repo skeleton, models, copy data, requirements, empty tests. Ask the candidate to fill `sample_timeline.csv`. |
| 0:20 to 1:00 | rules.py and tests: all E1 to E5 and W1 hashtag cases, episode ambiguity, no-number cases. |
| 1:00 to 1:30 | timeline.py, tags.py, decide.py with unit tests. |
| 1:30 to 2:10 | classify.py: keyword fallback, LLM call with schema, cache, flags. |
| 2:10 to 2:40 | evaluate.py, run it, write results and failure analysis. |
| 2:40 to 3:15 | Streamlit UI, deploy (Streamlit Community Cloud or Hugging Face Spaces). |
| 3:15 to 4:00 | README, write-up, AI usage note, time log, and video script outline. Stop at four hours. |

## 9. Stretch (only if ahead of schedule)

- Mocked second-franchise handling polish for W5.
- Show the signal ladder as a small visual in the UI.
- Export evaluation as CSV.

## 10. UI (app.py)

One page. Left: video fields (title, description, channel, post date, optional transcript), viewer progress input (One Piece chapter number plus an optional free-text second series). Buttons: "Check", plus a dropdown of the golden-set examples and one invalid-input example. Right: verdict badge, estimated horizon, confidence, rung used, evidence quotes, reasons, suggested creator tag, and a visible "Implemented / Mocked / Deferred" panel. Show a banner that the timeline and entity tables are sample data and results are not claims about real accuracy.

## 11. Demo cases for the walkthrough

1. Clear spoiler: E2 (live reaction, chapter in title), viewer at 1100.
2. Same video, viewer at 1196: SAFE.
3. Weak signal, hashtag only: W1.
4. Hard case: W5 (empty description, two franchises). Show RISKY, explanation, and mocked second series.
5. Invalid input: empty fields or bad date, showing the validation message.

## 12. Deliverables checklist

- [ ] Live prototype link
- [ ] Source code repo with tests passing
- [ ] README: setup, dependencies, sample data, example inputs and outputs, how to run offline with the cache, implemented/mocked/deferred table
- [ ] Write-up (max 4 pages), outline below
- [ ] Time spent (from TIME_LOG.md)
- [ ] What I would investigate next
- [ ] How AI was used and how it was checked (AI_USAGE.md)
- [ ] 5 to 10 minute video

### Write-up outline (4 pages max)
1. Three candidate problems (half page): the spoiler problem plus two short alternatives from the candidate's own experience (candidate to supply the other two) and why this one.
2. Observed vs assumed (half page), from section 2.
3. Current handling, smallest first step, rejected alternative, kill criterion (half page).
4. Design and why (1 page): signal ladder, why rules first, why LLM is limited, unknown defaults to risky.
5. Evaluation (1 page): table, failure analysis, limits of n.
6. Implemented / mocked / deferred (quarter page).
7. What I would investigate next (quarter page): a larger random sample, how many videos already label horizons, creator adoption, anime episode mapping, multilingual.
8. AI use and checking (quarter page).

### Video script outline (5 to 10 minutes)
Problem and story (1 min), observed vs assumed (1 min), demo cases 1 to 5 (4 min), evaluation and failures (2 min), limits and next steps (1 min).

### AI usage note (what to say, adjust to what actually happened)
Claude Code was used to scaffold code and tests. Checks: unit tests on each rule, the hand-labeled golden set, manual review of every LLM output against the source text, no plot or chapter facts accepted from the model, timeline and entity tables built by the candidate from public sources.

## 13. Open items for the candidate (do not block the build)

- Fill `sample_timeline.csv` from a public source.
- Fill gold labels for W2 to W5 in `golden_set.csv` (and verify W1).
- Decide the two other problem ideas for the write-up.
- Keep the time log honest, stop at four hours.
- Pending separately: reply to the MiraFlores recruiter about the legal entity, E-Verify, sponsorship and expected time commitment.

## 14. Decisions made during the build (2026-10-28)

- LLM provider is Groq, not Claude. Claude Code was used to write the code.
- Two viewer personas: catching up (any progress, e.g. 100, 400, 900) and current weekly readers (one chapter behind). Eval profiles: 100, 400, 900, 1100, 1150, 1190, 1195, 1196. Gold labels are computed from `gold_horizon_chapter` for any progress.
- Horizon is a range. Lower bound from content (explicit chapter, leak wording, recency cue, named entity). Upper bound from the post date. SPOILER if low > P, SAFE if high <= P, else RISKY.
- Leak window: 7 days. Observed in the golden set: E5 posted 5 days before 1195, E2/E3 2 days and E1 1 day before 1196.
- No video descriptions were collected. Eval input is title + hashtags recorded in the CSV.
- W2 to W5 gold horizons: latest official chapter on or before the post date (candidate judgment). W4 (2024-08-19) is 1123.
- Timeline: chapters 1100 to 1196 from official Shonen Jump listings and the One Piece wiki, supplied by the candidate.
- Entities: candidate's character reveal guide, with `match_terms` added. Ambiguous short terms (Ace, Dragon) replaced by full names.
