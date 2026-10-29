# Video script (about 5 minutes)

Setup before recording: two browser tabs. Tab 1: https://spoilerguard-onepiece.streamlit.app/ (loaded and awake). Tab 2: YouTube. Have docs/eval_results.md open in a third tab.

## 0:00 to 0:50 Where the idea came from

> "Hi, I'm Siddhesh. There's a huge audience for anime and manga discussion content on YouTube: reactions, chapter reviews, theories, power rankings. A lot of those viewers aren't caught up. They're working through a series and they enjoy the community content alongside it. I'm one of them. I read One Piece, I fall behind, and I love watching reactions and discussions as I go.
>
> The problem is that YouTube spoils you constantly. A title says 'Chapter 1196 live reaction'. A power ranking names a character you haven't met. A video with 'blind reaction' in the title sounds safe, but 'blind' means the creator hasn't read it, not you. And from the thumbnail and title, you can't tell whether a video is past where you are."

## 0:50 to 1:30 What the prototype is

> "There are two kinds of viewer here. Someone catching up, at chapter 100 or 900, who can be spoiled by almost anything, even old videos. And a weekly reader who's one chapter behind.
>
> The real product would be a browser extension that warns you as you scroll. Before building that, I wanted to test the core question: given what's visible about a video, can you tell whether it goes past my chapter? So this prototype is the decision engine. You paste a video's title, description and post date, enter your chapter, and it answers SAFE, SPOILER or RISKY, with the evidence. Pasting by hand isn't the product, it's how I test the logic. Fetching the data automatically, with the YouTube API or an extension, is the deferred plumbing."

## 1:30 to 3:30 Live demo

**Video 1: one with a chapter number.**

[Tab 2: search `one piece chapter reaction`. Open a recent video with a chapter number in the title.]

> "Here's a reaction video. I'll copy the title, the post date, and the description or hashtags."

[Copy the title. Expand the description, copy the first lines or hashtags. Note the date. If YouTube says "3 days ago", convert it to YYYY-MM-DD.]

[Tab 1: paste into Title, Description, Post date. Set chapter to 1100. Press Check.]

> "SPOILER, high confidence. It found the chapter number in the title, and it shows the exact quote it used. 'Decided by: explicit chapter.' It also suggests a label the creator could add."

[Change the chapter to that video's chapter number or higher. Press Check.]

> "Same video, but now I'm caught up: SAFE. The verdict depends on the viewer, not just the video."

**Video 2: one without a chapter number.**

[Tab 2: search `one piece strongest characters` or `shanks vs mihawk`. Pick one with no chapter number.]

[Paste it in. Set chapter to 100, press Check. Then 1100.]

> "No chapter number here. For a reader at chapter 100, it may still say SPOILER, because the title names a character who first appears later, and I gave it a small table of first appearances. For a reader at 1100, it says RISKY: the post date caps how far the video could go, but nothing in the text proves where it stops. When the tool doesn't know, it says RISKY, never SAFE. Missing a spoiler is worse than an extra warning."

[Open the "Signal ladder" expander.]

> "This is the order it checks things in: explicit chapter numbers first, then leak wording, then recency words, then character names, then the post date. The LLM only labels the video's format. It never decides chapters or plot, because it can't know recent chapters and would make them up."

**Invalid input.**

[Pick "INVALID: empty title, bad date" from the example dropdown. Press Check.]

> "And bad input gets a clear message instead of a guess."

## 3:30 to 4:30 How well it works

[Tab 3: docs/eval_results.md]

> "I hand-labeled 10 videos and tested each one at 8 reading positions, so 80 cases. It warned on all 62 spoiler cases and raised 2 false alarms out of 18 safe ones. A 'warn on everything' baseline gets 18 false alarms.
>
> Three honest caveats. First, the easy videos with chapter numbers are solved. The weak-signal ones only get a firm answer in 15 of 40 cases; the rest are RISKY. Second, the LLM classifier added nothing measurable on this data, because I only had titles. Third, ten hand-picked videos isn't a sample, so these are counts, not accuracy claims."

## 4:30 to 5:00 Next steps

> "Next, I'd take a random sample of a hundred videos after a release and check how many already label their chapter. If most do, the tool isn't worth building, and that's my kill criterion. Then descriptions and transcripts, anime episode mapping, and non-English videos. Thanks for watching."

## Tips for the live demo

- Videos posted after Oct 18, 2026 may show "beyond timeline coverage", because the release table ends at Ch. 1196. That's expected; say so if it appears.
- Wake the app before recording. Streamlit Cloud apps sleep and take about 30 seconds to start.
- If a live video gives an odd result, fall back to the dropdown examples (E2, W4, W5). Their results are known.
