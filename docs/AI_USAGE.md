# How AI was used and how it was checked

## Two different uses

1. **Claude Code (building).** Generated the code, tests, eval script, UI and first drafts of these docs from the plan in CLAUDE.md. Design decisions were made in conversation: two viewer personas, horizon as a range, Groq as the runtime LLM, gold labels for W2 to W5.
2. **Groq `openai/gpt-oss-120b` (runtime).** Classifies only the video format and quotes recency words. Never asked about plot, chapters or release dates.

## What was not taken from AI

- Release dates (`sample_timeline.csv`): supplied by the candidate from official Shonen Jump listings and the One Piece wiki. Claude Code only parsed the pasted text and checked that chapters are consecutive and dates increase.
- Character first chapters (`sample_entities.csv`): supplied by the candidate. Claude Code added match terms and removed ambiguous short names ("Ace", "Dragon").
- Gold labels: the candidate's judgment. Claude Code computed per-profile labels from the horizon and checked them against the stored columns.

## Checks

- **Unit tests:** 55 tests, one or more per rule, including every golden-set title, episode ambiguity, word boundaries, leak window, cache use without API, API failure fallback, invalid input.
- **Golden set:** 10 hand-labeled videos x 8 viewer profiles. Shuffle sanity check: accuracy drops from 0.97 to about 0.84 when gold horizons are shuffled.
- **Bugs found by checking, not by the AI:** a bare-number pattern also matched inside `#onepiece1132`, upgrading a hashtag to an explicit chapter (fixed, test added). The first date-cap version would have rated E2 as horizon 1195 because it was posted 2 days before 1196's official date (fixed with the leak window, test added).
- **Manual review of every Groq output against the source text** (2026-10-28):

| id | Title | LLM format | Correct? |
|---|---|---|---|
| E1 | YAPPPING One Piece Chapter 1196 w/ Tier 3 (short) | ranking | **No**, it is a discussion. "Tier 3" is a membership tier, not a tier list. No effect on the verdict (chapter number decides) |
| E2 | One Piece Manga Chapter 1196 LIVE Reaction | live_reaction | Yes |
| E3 | ONE PIECE 1196 BLIND READING REACTION | reading | Yes (streamed reading reaction) |
| E4 | Chapter 1196 [One Piece] - MelonTeee | reading | Plausible (gold: live reading reaction); not inferable from the title alone |
| E5 | ONE PIECE CHAPTER 1195 - FIRST CONFIRMED SPOILER | leak, unreleased=true | Yes |
| W1 | ENDING THE DEBATE: Top 30 Strongest One Piece Characters! | ranking | Yes |
| W2 | King Of Lightning Reacts To Shanks VS Mihawk Is Simple! | reaction | Yes |
| W3 | The World Greatest Swordsman Mihawk Who Beat Shanks... | ranking | Acceptable (gold: power-scaling argument) |
| W4 | Blackbeard's WEAKEST LINK Might Be His SECRET Weapon! | theory | Yes |
| W5 | So Naruto vs Luffy is Happening... | versus | Yes |

8 of 10 correct, 1 plausible, 1 wrong. The LLM returned no temporal cues for any video; the keyword list found "FIRST CONFIRMED" (E5) and "is Happening" (W5). No hallucinated cues had to be dropped.

## Prompt-injection handling

Video text is untrusted. It is wrapped in `<video>` tags, the system prompt says to treat it as data, JSON mode is on, the output is validated against a fixed schema (format enum, list of strings, boolean), and quoted cues must be exact substrings of the input. Invalid output is retried once, then the keyword classifier is used. Even a fully hijacked model can only change the format label and cue list, and the decision layer never takes a chapter number from the model.
