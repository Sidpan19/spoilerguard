# Video script (about 5 minutes)

Setup: tab 1 the app (https://spoilerguard-onepiece.streamlit.app/, wake it before recording), tab 2 YouTube, tab 3 docs/eval_results.md.

## 0:00 to 0:20 Intro

> "Hi, I'm Siddhesh Pande. This is my case study for the AI Engineer role at MiraFlores AI. The brief was to pick a real problem from my own experience, frame it honestly, and build a small working prototype. I'll walk through the problem, demo the prototype live, and talk about how well it works and where it falls short."

## 0:20 to 1:30 The problem

> "There's a huge audience for anime and manga discussion content on YouTube: reactions, reviews, theories, and especially power-scaling and character videos. 'Who's stronger, Shanks or Mihawk?' 'Top 30 strongest characters.' A lot of the people watching aren't caught up. They're working through a series and enjoy the community content alongside it. I'm one of them. I'm reading One Piece and I watch these videos as I go.
>
> Videos with a chapter number in the title are easy: you see 'Chapter 1196' and you skip it. The real trap is the power-scaling and character videos. The title is just two names. The description is vague, or empty, or a few hashtags. There's no chapter number anywhere. But to argue who's stronger, the creator uses every fight, every reveal, every power-up up to the latest chapter. So a video that looks like harmless debate can spoil years of story for someone catching up, and you can't tell from the surface."

## 1:30 to 2:00 What the prototype is

> "The full product would be a browser extension that warns you as you scroll. Before building that, I wanted to test the core question: from what's visible about a video, can you tell whether it goes past my chapter? So this prototype is the decision engine. You paste a video's title, description and post date, enter your chapter, and it says SAFE, SPOILER or RISKY, with the evidence. Pasting by hand isn't the product. It's how I test the logic."

## 2:00 to 3:45 Live demo: one Mihawk vs Shanks video

[Tab 2: search `shanks vs mihawk`. Open a power-scaling video.]

> "Here's a typical one. Title is two names, no chapter number. Let's look at the description."

[Expand the description. Copy title and description. Note the post date; convert "x days ago" to YYYY-MM-DD.]

> "Vague. Nothing here tells me how far into the story this goes."

[Tab 1: paste title, description, date.]

**Reader at chapter 30.** [Set chapter 30, press Check.]

> "SPOILER. It found 'Mihawk' and knows from a small table I built that Mihawk first appears in chapter 49. So for someone at chapter 30, just naming him is already past where they are."

**Reader at chapter 1100.** [Set chapter 1100, press Check.]

Say whichever one you see:

- **RISKY** (most likely):
  > "RISKY. The post date tells it the video can't go past the latest chapter, but nothing in the text proves where it stops. It could cover the newest fights, or it could be about old ones. When the tool doesn't know, it says RISKY, never SAFE, because missing a spoiler is worse than an extra warning. This is exactly the vague power-scaling case I described."

- **SPOILER** (if the description names a late reveal, e.g. Shamrock):
  > "SPOILER. The description mentions Shamrock, which is a reveal from chapter 1134, so the video is at least that far."

- **SAFE** (if the video is old):
  > "SAFE, because it was posted when only chapters up to N existed."

[Open the "Signal ladder" expander.]

> "This is the order it checks things in: an explicit chapter number, leak wording, recency words, character names, and finally the post date. The AI model only labels the video's format, like 'versus' or 'reaction'. It never decides chapters or plot, because it can't know recent chapters and would make them up. Every number in a verdict comes from the text or from tables I supplied."

[Point at the suggested tag.]

> "It also suggests a label the creator could add, so the fix could come from creators too."

## 3:45 to 4:30 How well it works

[Tab 3: eval results]

> "I hand-labeled 10 videos and tested each at 8 reading positions, from chapter 100 to 1196. That's 80 cases. It warned on all 62 spoiler cases, with 2 false alarms out of 18 safe ones. A 'warn on everything' baseline gets 18 false alarms.
>
> Honestly though: videos with chapter numbers are solved. The vague ones, like the one I just showed, only get a firm SAFE or SPOILER in 15 of 40 cases. The rest are RISKY. And 10 hand-picked videos is not a sample, so these are counts, not accuracy claims. My next step would be a random sample of a hundred videos to see how many already label their chapter. If most do, this isn't worth building."

## 4:30 to 5:00 Where this could go

> "Nothing here is specific to One Piece except two tables: release dates and character first appearances. Swap those and you get SpoilerGuard for Naruto, for Jujutsu Kaisen, or for TV shows like Game of Thrones, where episodes replace chapters. Thanks for watching."

## Tips

- Wake the app before recording; a sleeping Streamlit app takes about 30 seconds.
- Try your Mihawk vs Shanks video once before recording so you know which verdict appears at 1100.
- A video posted after Oct 18, 2026 shows a horizon up to Ch. 1197 ("beyond timeline coverage") because the table ends at 1196. That's expected.
- If the brief's "invalid input" demo is wanted, add 10 seconds: pick "INVALID: empty title, bad date" in the dropdown and press Check.
