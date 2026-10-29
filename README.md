# SpoilerGuard

Checks whether a One Piece YouTube video is likely to spoil a viewer, given the video's pasted metadata and the viewer's manga progress. Returns SAFE, RISKY or SPOILER, an estimated chapter horizon, the evidence, and a suggested label the creator could add.

Case study prototype for MiraFlores AI. Small on purpose: one franchise, English, pasted input, 10 hand-labeled videos.

- Live prototype: https://spoilerguard-onepiece.streamlit.app/
- Source: https://github.com/Sidpan19/spoilerguard
- Write-up: [docs/WRITEUP.md](docs/WRITEUP.md)
- Evaluation: [docs/eval_results.md](docs/eval_results.md)
- Time log: [docs/TIME_LOG.md](docs/TIME_LOG.md), AI usage: [docs/AI_USAGE.md](docs/AI_USAGE.md)

## How it works

The video's horizon (the latest chapter it could reveal) is treated as a range.

- **Lower bound** comes from the content: an explicit chapter number ("Chapter 1196", "#onepiece1132"), leak wording, a recency cue in a reaction or discussion video, or a named character whose first chapter is known.
- **Upper bound** comes from the post date: a video cannot discuss a chapter that was not out or leaking yet. Leaks circulate before the official date, so the cap uses a 7-day leak window (observed in the golden set: 1 to 5 days early).

For viewer progress P: low > P is **SPOILER**, high <= P is **SAFE**, anything else is **RISKY**. Unknowns never default to SAFE.

The LLM (Groq) only labels the video format and quotes recency words. It is never asked about plot or chapters, its output is schema-checked, and any quoted cue not found in the input is dropped.

## Setup

Python 3.11+.

```bash
pip install -r requirements.txt
python -m pytest -q                 # 55 tests
python -m src.evaluate              # writes docs/eval_results.md and .csv
streamlit run app.py                # UI
```

**Runs offline with no API key.** LLM outputs for the 10 sample videos are cached in `data/llm_cache.json`. For new pasted text, the app calls Groq only if `GROQ_API_KEY` is set; otherwise it uses the keyword classifier and says so.

Optional:

```bash
export GROQ_API_KEY=...             # PowerShell: $env:GROQ_API_KEY="..."
export GROQ_MODEL=openai/gpt-oss-120b   # default
python -m src.cli --build-cache --refresh-cache   # re-classify the golden set
```

Deploying on Streamlit Community Cloud: point it at `app.py`, add `GROQ_API_KEY` under App settings > Secrets (see `.streamlit/secrets.toml.example`). Never commit the key.

## Dependencies

`streamlit`, `groq`, `pytest`. Everything else is the standard library.

## Sample data (`data/`)

| File | What | Source |
|---|---|---|
| `golden_set.csv` | 10 videos: 5 explicit (E), 5 weak-signal (W), with gold horizons | Metadata pasted by the author. No descriptions were collected; only titles and the hashtags noted. W2 to W5 horizons are the author's judgment (latest chapter on or before the post date) |
| `sample_timeline.csv` | Chapters 1100 to 1196 with official release dates | SAMPLE, supplied by the author from official Shonen Jump listings and the One Piece wiki |
| `sample_entities.csv` | 20 characters with first-appearance chapters | SAMPLE, the author's reveal guide. Not independently verified |
| `llm_cache.json` | Groq classifier outputs for the 10 videos | Generated 2026-10-28, `openai/gpt-oss-120b`, each manually reviewed |

No real viewer data is stored.

## Example inputs and outputs (CLI)

```
$ python -m src.cli --golden E2 --progress 1100      # "One Piece Manga Chapter 1196 LIVE Reaction"
Verdict:    SPOILER  (confidence high)
Horizon:    Ch. 1196
Rung:       1 explicit chapter
Suggested creator tag: Manga spoilers up to Ch. 1196

$ python -m src.cli --golden E2 --progress 1196
Verdict:    SAFE  (confidence high)

$ python -m src.cli --golden W4 --progress 100       # "Blackbeard's WEAKEST LINK...", 2024-08-19
Verdict:    SPOILER  (confidence medium)
Horizon:    Ch. 223 to 1124
Rung:       4 named entity
  - Names Blackbeard, who first appears in Ch. 223: horizon is at least that.
  - Posted when at most Ch. 1124 could be out or leaking.

$ python -m src.cli --golden W5 --progress 1195 --other-series Naruto ep200   # "So Naruto vs Luffy is Happening..."
WARNING: 'Naruto' is not supported; its result is MOCKED (always RISKY).
Verdict:    RISKY  (confidence low)
Horizon:    Ch. ? to 1197
Other series: Naruto: RISKY (MOCKED: no rules or release data for Naruto (your progress: ep200).)

$ python -m src.cli --title "" --date 16/10/2026 --progress abc
INVALID INPUT: Title and description are both empty. Paste at least the video title.
INVALID INPUT: Post date '16/10/2026' is not a valid date. Use YYYY-MM-DD.
INVALID INPUT: One Piece progress must be a chapter number, got 'abc'. Anime episode progress is not supported yet.
```

Free text: `python -m src.cli --title "..." --description "..." --date 2026-10-16 --progress 1100`. Add `--no-llm` for the keyword classifier only.

## Results (summary)

80 cases (10 videos x 8 viewer profiles). Full table and failure analysis in [docs/eval_results.md](docs/eval_results.md).

| System | Spoilers warned | False alarms | Firm verdict (SAFE/SPOILER) | Firm verdicts correct |
|---|---|---|---|---|
| Rules + LLM classifier | 62/62 | 2/18 | 55/80 | 55/55 |
| Warn on everything | 62/62 | 18/18 | 0/80 | n/a |

Rules only and rules + keyword classifier score the same as the LLM version on this set. n = 10 videos; these numbers do not generalize.

## Implemented, mocked, deferred

| | |
|---|---|
| **Implemented** | One Piece manga chapters, English, pasted metadata. Regex rules, date bounds with leak window, character lower bounds, Groq classifier with schema check, retry and keyword fallback, cache, creator tag, input validation, CLI, Streamlit UI, evaluation with 4 systems and a shuffle sanity check |
| **Mocked** | Any second franchise (detected by name, always RISKY, labeled MOCKED). LLM outputs for the sample videos come from the cache |
| **Deferred** | YouTube API or scraping. Following the linked original in reaction videos (W2). Non-English. Anime episode to chapter mapping. Comments and live chat. Thumbnails and OCR. Creator-side plugin. Accuracy on a real random sample |

## Layout

```
src/models.py     dataclasses
src/validate.py   input checks and messages
src/rules.py      chapter / hashtag / episode / warning / entity / franchise regexes
src/timeline.py   release table, date bounds, leak window
src/classify.py   keyword classifier, Groq call, cache
src/decide.py     horizon range and verdict
src/tags.py       creator tag
src/evaluate.py   metrics, failure analysis, shuffle check
src/cli.py        command line
app.py            Streamlit UI
tests/            55 tests
```
