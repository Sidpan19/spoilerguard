# Video script outline (target 8 minutes)

## 1. Problem and story (1 min)
- I read One Piece weekly and fall behind. YouTube titles and summaries spoil chapters I have not read.
- Show a search results page screenshot: chapter numbers, "blind reaction", leak titles.
- Two viewers: someone catching up (Ch. 100 to 1100) and a weekly reader one chapter behind.

## 2. Observed vs assumed (1 min)
- Observed: chapter numbers in titles, "blind" means the creator, leaks 1 to 5 days before release, old videos still spoil catch-up readers, weak-signal videos.
- Assumed: fans want per-series progress, creators would add labels, my 10 videos are representative (they are not).

## 3. Demo (4 min), in the app
1. **E2, progress 1100:** SPOILER, high, Ch. 1196 quoted from the title. Point at "Decided by" and the evidence.
2. **E2, progress 1196:** SAFE. Same video, different viewer.
3. **W1, progress 1100:** SPOILER from the hashtag only, medium confidence, episode caveat. Change to 1150: SAFE.
4. **W4, progress 100 then 1196:** Blackbeard gives SPOILER for the catch-up reader; the 2024 date gives SAFE for the current reader. Open the signal ladder.
5. **W5, progress 1195, second series Naruto:** RISKY, low, MOCKED Naruto line. Explain why: no number, no description, posted after 1196.
6. **Invalid example:** empty title and bad date. Clear messages, nothing checked.

## 4. Evaluation and failures (2 min)
- Open docs/eval_results.md. 80 cases. 0 missed spoilers, 2 false alarms vs 18 for warn-everything.
- Weak videos: only 15/40 firm verdicts.
- Be candid: the LLM added nothing measurable here; weak-signal gold labels share the release table with the tool; n = 10.
- Show the LLM review table: 1 wrong format label, no effect.

## 5. Limits and next steps (1 min)
- Deferred list. Next: random sample to test the kill criterion, independent labels, descriptions and transcripts, episode mapping, non-English.
