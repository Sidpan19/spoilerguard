# SpoilerGuard: telling whether a YouTube video will spoil your manga

Siddhesh Pande. MiraFlores AI case study. Prototype: https://spoilerguard-onepiece.streamlit.app/. Code: https://github.com/Sidpan19/spoilerguard.

## 1. Three problems

1. **Spoilers from YouTube (chosen).** I read One Piece weekly and sometimes fall behind. YouTube titles, thumbnails, descriptions and auto-summaries reveal plot, and I cannot tell from the surface whether a video is past my chapter.
2. `<candidate: second problem from personal experience, 2 to 3 lines>`
3. `<candidate: third problem, 2 to 3 lines>`

**Why this one:** `<candidate: e.g. I hit it every week, I could collect real examples in an hour, and the core decision (horizon vs progress) is small enough to build and evaluate honestly in 4 hours.>`

## 2. Observed vs assumed

**Observed** (my experience and 10 collected videos):
- Explicit leaks are common: chapter numbers in titles of live reactions and readings (E1 to E4).
- "Blind reaction" describes the creator, not the viewer. A blind reaction to Ch. 1196 still spoils someone at 1100.
- Leak videos point past the latest release. E5 posted a "confirmed spoiler" for Ch. 1195 five days before its official date. Reactions to Ch. 1196 appeared 1 to 2 days before its official date.
- Weak-signal videos exist: no chapter number, a lone hashtag (W1), a reaction to another creator's video (W2), character names only (W4), two franchises and an empty description (W5).
- Old videos still spoil people catching up. A 2024 video naming Blackbeard spoils a reader at Ch. 100.
- Many results are not in English.

**Assumed** (not verified):
- Fans want per-series progress settings rather than a global spoiler filter.
- Creators would adopt a suggested label if it were easy.
- The 10 videos reflect the wider distribution. They do not: they are a hand-picked seed, not a random sample.
- Anime episode vs manga chapter confusion is common (anecdotal).

## 3. Today, first step, rejected alternative, kill criterion

**Today:** muting keywords, avoiding YouTube after a release, trusting creator warnings, watching only trusted creators, forum spoiler tags. All manual and coarse, and all fail on weak-signal videos.

**Smallest first step:** a checker over pasted metadata for one franchise (One Piece manga chapters), evaluated on a hand-labeled set. No scraping, no browser extension.

**Rejected:** "ask an LLM whether this is a spoiler". An LLM cannot know chapters released after its training, will invent horizons, and cannot be audited. Here the LLM only labels the video's format.

**Kill criterion:** stop if, in a larger random sample, most videos already state their horizon clearly (chapter number or warning), or if weak-signal videos cannot be separated from safe ones better than a "warn on every reaction or live video" baseline.

## 4. Design

Two kinds of viewer drive the design. **Catching up** readers (at Ch. 100, 400, 900) are spoiled by almost anything, including old videos and character names. **Weekly** readers one chapter behind are spoiled only by the newest chapter.

So the video's horizon is a **range**, not a guess:

- **Lower bound from content**, strongest first: explicit chapter number; leak wording (next unreleased chapter); a recency cue ("new chapter", "this week") in a reaction, reading or discussion video (latest chapter at post date); a named character with a known first chapter (user-supplied table).
- **Upper bound from the post date**: nothing can be discussed that was not out or leaking. A 7-day leak window covers the 1 to 5 days observed.

Verdict for progress P: low > P is SPOILER, high <= P is SAFE, otherwise RISKY. No signal means RISKY, never SAFE. Missing a spoiler costs more than an extra warning.

**Why rules first.** Every number in a verdict comes from the input text or from tables I supplied (release dates from Shonen Jump and the One Piece wiki, first appearances from my own guide). Each verdict shows its quoted evidence and which rule decided it, so it can be audited.

**Why the LLM is limited.** Groq (`gpt-oss-120b`) returns only a format label, recency words and a leak flag, in JSON checked against a schema. Recency words must be exact substrings of the input. Video text is untrusted: it is wrapped in delimiters and the model is told to treat it as data. A hijacked model can only change a format label, and no chapter number ever comes from the model. Invalid output is retried once, then a keyword classifier is used. Outputs are cached so the demo runs without a key.

**Invalid input** (empty title, bad date, non-numeric progress, too long) returns clear messages and no verdict. A second franchise is detected and shown as RISKY, labeled MOCKED.

## 5. Evaluation

10 videos x 8 viewer profiles (100, 400, 900, 1100, 1150, 1190, 1195, 1196) = 80 cases. Gold: spoiler if the video's horizon > progress. Input is title plus recorded hashtags only (I did not collect descriptions). "Warn" = SPOILER or RISKY.

| System | Spoilers warned | False alarms | Firm verdicts | Firm verdicts correct |
|---|---|---|---|---|
| (a) Rules only | 62/62 | 2/18 | 55/80 | 55/55 |
| (b) Rules + keyword classifier | 62/62 | 2/18 | 55/80 | 55/55 |
| (c) Rules + LLM classifier | 62/62 | 2/18 | 55/80 | 55/55 |
| (d) Warn on everything | 62/62 | 18/18 | 0/80 | n/a |

By group: explicit videos get a firm, correct verdict in 40/40 cases. Weak-signal videos only in 15/40; the rest are RISKY. For current readers, false alarms drop from 16/16 (baseline) to 2/16.

**Failures.** No spoiler was missed. Two false alarms: W3 and W5 for a reader at 1196. Both were posted after Ch. 1196's release date, my timeline ends at 1196, so the tool cannot rule out that 1197 was already leaking, and returns RISKY. That is the intended behaviour, not a bug.

**What the numbers do not show:**
- **The classifier added nothing measurable.** All three systems tie. None of the titles contains a recency cue in a reaction-type video, so the format label never changes a verdict. Its value would show on descriptions and transcripts, which I did not collect.
- **Weak-signal gold labels are not independent.** I set W2 to W5 horizons to the latest chapter at the post date, and the tool's upper bound uses the same release table. The SAFE verdicts for those videos are partly guaranteed by construction. Independent labels would need someone to watch the videos.
- **W2's real horizon is hidden** in the linked original video. **W1's hashtag** may be an anime episode, not a chapter.
- **n = 10, hand-picked.** Counts, not rates. A shuffle test confirms the eval is wired correctly (accuracy 0.97 vs 0.84 with shuffled labels), not that the tool generalizes.
- Manual review of the LLM: 8 of 10 format labels correct, 1 plausible, 1 wrong (read "Tier 3" membership as a tier list). It did not affect any verdict.

## 6. Implemented, mocked, deferred

- **Implemented:** One Piece manga, English, pasted metadata; rules, date bounds, character bounds, Groq classifier with schema check and fallback, cache, creator tag, validation, CLI, Streamlit UI, evaluation, 55 tests.
- **Mocked:** any second franchise (always RISKY); cached LLM outputs for the samples.
- **Deferred:** YouTube API or scraping; following linked originals; non-English; anime episode mapping; comments and live chat; thumbnails/OCR; creator plugin; accuracy on a random sample.

## 7. What I would investigate next

1. A random sample of 100+ videos after a release: how many already state their horizon? This tests the kill criterion directly.
2. Independent labels for weak-signal videos, from watching them, to break the circularity above.
3. Descriptions and transcripts: does the classifier then earn its place?
4. Anime episode to chapter mapping, since many viewers track the anime.
5. Non-English titles, which were a large share of what I saw.
6. Whether creators would use a suggested label: ask 5 to 10 small creators.

## 8. AI use and checking

Claude Code wrote the code, tests and first drafts of the docs from my plan, and I directed the design decisions (personas, range-based horizon, Groq, gold labels). Groq is the runtime classifier. Nothing factual came from AI: release dates and character first chapters are tables I supplied from public sources; gold labels are my judgment. Checks: 55 unit tests, the golden-set eval with a shuffle test, and a manual review of every LLM output against the source title (table in AI_USAGE.md). Two bugs were caught this way: a hashtag being read as an explicit chapter, and a reaction posted before the official date being capped one chapter too low.
