"""Streamlit UI: streamlit run app.py"""
from __future__ import annotations

import os

import streamlit as st

from src.decide import check
from src.evaluate import load_golden
from src.models import ONE_PIECE, VideoInput

st.set_page_config(page_title="SpoilerGuard", layout="wide")

# Streamlit Cloud secrets -> env, so classify.py sees the key. Never shown in the UI.
try:
    if "GROQ_API_KEY" in st.secrets and not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

GOLDEN, _ = load_golden()
EXAMPLES = {"(paste your own)": None}
for g in GOLDEN:
    EXAMPLES[f"{g.video.id}: {g.video.title[:60]}"] = g.video
EXAMPLES["INVALID: empty title, bad date"] = VideoInput(title="", description="", post_date="16/10/2026")

LADDER = [
    ("1", "Explicit chapter number (title, description, hashtag)"),
    ("2", "Spoiler / leak wording"),
    ("3", "Post date + recency cue in a reaction/reading/discussion video"),
    ("4", "Named character with a known first chapter"),
    ("date cap", "Post date: nothing past the latest chapter out or leaking"),
    ("5", "Risky format, no horizon"),
    ("6", "Unknown: defaults to RISKY"),
]
BADGE = {"SAFE": ("#1b7f3b", "SAFE"), "RISKY": ("#b26a00", "RISKY"), "SPOILER": ("#b3261e", "SPOILER")}

st.title("SpoilerGuard")
st.caption("Is this One Piece YouTube video a spoiler for where you are in the manga?")
st.markdown("Paste a video's title and date, enter your chapter, press **Check**.")
st.warning("Prototype. Timeline and character tables are SAMPLE data supplied by the author. "
           "Results come from 10 hand-labeled videos and are not claims about real-world accuracy.")

left, right = st.columns([1, 1], gap="large")

with left:
    choice = st.selectbox("Load an example", list(EXAMPLES.keys()))
    ex = EXAMPLES[choice]
    key = choice  # reset fields when the example changes
    title = st.text_input("Video title", value=ex.title if ex else "", key=f"t{key}")
    description = st.text_area("Description", value=ex.description if ex else "", height=100, key=f"d{key}",
                               help="Golden-set examples only have hashtags here; no descriptions were collected.")
    channel = st.text_input("Channel", value=ex.channel if ex else "", key=f"c{key}")
    post_date = st.text_input("Post date (YYYY-MM-DD)", value=ex.post_date if ex else "", key=f"p{key}")
    transcript = st.text_area("Transcript excerpt (optional)", value="", height=68, key=f"x{key}")
    st.markdown("**Your progress**")
    c1, c2, c3 = st.columns([1, 1, 1])
    progress = c1.text_input("One Piece: last chapter read", value="1100")
    other_name = c2.text_input("Second series (mocked)", value="")
    other_prog = c3.text_input("Its progress (free text)", value="")
    use_llm = st.checkbox("Use LLM classifier (cached for examples; live Groq call only for new text if a key is set)",
                          value=True)
    run = st.button("Check", type="primary")

with right:
    if run:
        video = VideoInput(title=title, description=description, channel=channel,
                           post_date=post_date, transcript_excerpt=transcript, id=ex.id if ex else None)
        raw = {ONE_PIECE: progress}
        if other_name.strip():
            raw[other_name.strip()] = other_prog
        v, d, s = check(video, raw, mode="llm" if use_llm else "keyword")
        for w in v.warnings:
            st.warning(w)
        if not v.ok:
            st.error("Invalid input. Nothing was checked.")
            for e in v.errors:
                st.markdown(f"- {e}")
        else:
            color, label = BADGE[d.verdict]
            st.markdown(f"<div style='background:{color};color:white;padding:14px 18px;border-radius:8px;"
                        f"font-size:28px;font-weight:700'>{label}</div>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Estimated horizon", d.horizon_text())
            m2.metric("Confidence", d.confidence)
            m3.metric("Your progress", f"Ch. {v.progress.one_piece}")
            st.markdown(f"**Decided by:** {d.rung}")

            st.markdown("**Why**")
            for r in d.reasons:
                st.markdown(f"- {r}")
            st.markdown("**Evidence (quoted from the input)**")
            if d.evidence:
                for e in d.evidence:
                    st.markdown(f"- `{e.source}`: \"{e.quote}\" ({e.detail})")
            else:
                st.markdown("- none")
            if d.other_series:
                st.markdown("**Other series (MOCKED)**")
                for o in d.other_series:
                    st.markdown(f"- {o.series}: **{o.verdict}**. {o.reason}")
            st.info(f"Suggested creator tag: **{d.suggested_tag}**")

            with st.expander("Signal ladder"):
                for k, text in LADDER:
                    hit = d.rung.startswith(k) if k != "date cap" else d.rung == "date cap"
                    st.markdown(f"{'**> ' if hit else '&nbsp;&nbsp;&nbsp;'}{text}{'**' if hit else ''}")
            with st.expander("Classifier output"):
                c = s.classification
                st.write({"source": c.source, "format": c.format, "temporal_cues": c.temporal_cues,
                          "references_unreleased": c.references_unreleased, "notes": c.notes})
                st.caption("The LLM only labels format and quotes cue words. It is never asked about plot.")
    else:
        st.info("Pick an example or paste a video's metadata, set your chapter, and press Check.")

    with st.expander("Implemented / Mocked / Deferred", expanded=not run):
        st.markdown(
            "**Implemented:** One Piece manga chapters, English metadata pasted by hand; regex rules; "
            "release-date bounds with a 7-day leak window; character first-appearance lower bounds; "
            "Groq LLM format classifier with schema checks and keyword fallback; creator tag; input validation; "
            "evaluation on 10 hand-labeled videos.\n\n"
            "**Mocked:** any second franchise (always RISKY, labeled); LLM results for the examples come from a "
            "cache so the demo runs without a key.\n\n"
            "**Deferred:** YouTube API or scraping; following linked original videos; non-English; anime episode "
            "to chapter mapping; comments and live chat; thumbnails/OCR; creator plugin; accuracy beyond the sample.")
