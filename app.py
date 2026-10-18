from pathlib import Path

import pandas as pd
import streamlit as st
from google import genai


st.set_page_config(
    page_title="CreatorPulse AI",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1120px; padding-top: 2.2rem; padding-bottom: 4rem;}
      .hero {padding: 1.5rem 1.7rem; border-radius: 20px;
             background: linear-gradient(120deg, #101b3f 0%, #263f78 58%, #7358a6 100%);
             color: white; margin-bottom: 1.4rem;}
      .hero h1 {color: white; margin: 0 0 .35rem 0; font-size: 2.25rem;}
      .hero p {color: #e5eaff; margin: 0; font-size: 1.03rem;}
      .section-note {color: #68738a; margin-top: -.5rem;}
      [data-testid="stMetric"] {background: #f5f7fc; padding: 1rem; border-radius: 14px;}
      div.stButton > button[kind="primary"] {border-radius: 10px; padding: .65rem 1.2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🎬 CreatorPulse AI</h1>
      <p>Turn creator insights and trend inspiration into short-form video ideas.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "A creative copilot for personalized content planning. Trend records below are "
    "simulated examples, not live social media data."
)

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    client = None

st.header("👤 Build your creator profile")
st.markdown(
    '<p class="section-note">Tell us who you create for and how you like to tell stories.</p>',
    unsafe_allow_html=True,
)

profile_left, profile_right = st.columns(2)
with profile_left:
    creator_name = st.text_input(
        "Creator name",
        placeholder="e.g. NYC Student Creator",
    )
    content_niche = st.selectbox(
        "Content niche",
        ["Lifestyle", "Education", "Technology", "Fashion", "Food", "Travel", "Entertainment"],
    )
with profile_right:
    target_audience = st.text_input(
        "Target audience",
        placeholder="e.g. International students aged 18–24",
    )
    content_style = st.selectbox(
        "Content style",
        ["Authentic", "Funny", "Educational", "Inspirational", "Storytelling"],
    )

try:
    trends_df = pd.read_csv(Path(__file__).with_name("trends.csv"))
except Exception as error:
    st.error(f"The simulated trend dataset could not be loaded: {error}")
    st.stop()

with st.expander("📊 Explore the simulated trend examples"):
    st.caption("Sample data for product testing. These are not real-time or verified trends.")
    st.dataframe(trends_df, width="stretch", hide_index=True)

analyze = st.button("✨ Generate my content ideas", type="primary", width="stretch")

if analyze:
    if not creator_name.strip() or not target_audience.strip():
        st.warning("Please enter both your creator name and target audience.")
        st.stop()
    if client is None:
        st.error("Gemini is not configured. Add GEMINI_API_KEY in the app's Secrets settings.")
        st.stop()

    audience_query = target_audience.strip().lower()
    audience_matches = trends_df["audience"].fillna("").str.lower().apply(
        lambda audience: audience in audience_query or audience_query in audience
    )
    matched_trends = trends_df[
        (trends_df["niche"].str.casefold() == content_niche.casefold())
        & (trends_df["style"].str.casefold() == content_style.casefold())
        & audience_matches
    ].sort_values(by="popularity_score", ascending=False)

    st.divider()
    st.header("Your creator snapshot")
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Niche", content_niche)
    metric_b.metric("Audience", target_audience)
    metric_c.metric("Style", content_style)

    st.header("🎯 Trend inspiration")
    if matched_trends.empty:
        st.info(
            "No exact simulated trend matched all your profile details. "
            "Gemini will still create ideas from your niche, audience, and style."
        )
        trend_context = (
            "No simulated trend matched this profile. Create ideas from the creator profile alone; "
            "do not invent or imply a real-time trend."
        )
        source_note = "Ideas generated from your profile; no simulated trend matched."
    else:
        st.dataframe(matched_trends, width="stretch", hide_index=True)
        top_trend = matched_trends.iloc[0]
        trend_context = (
            f'Simulated trend: {top_trend["trend_name"]}\n'
            f'Description: {top_trend["description"]}\n'
            f'Simulated popularity score: {top_trend["popularity_score"]}'
        )
        source_note = (
            f'Inspired by simulated example: {top_trend["trend_name"]}. '
            "This is not a live or verified social media trend."
        )

    ai_prompt = f"""
You are a thoughtful creative strategist for short-form video.
Use simulated trend data only as inspiration. Never claim it is live, current, or verified.

Creator: {creator_name}
Niche: {content_niche}
Target audience: {target_audience}
Style: {content_style}
Trend context: {trend_context}

Create exactly 3 distinct original video ideas, personalized to this creator.
For each idea, provide a concise title, opening hook, core concept, three-beat outline,
and call to action. Format with clear headings and readable Markdown.
"""

    st.header("✨ Your AI-generated content ideas")
    try:
        with st.spinner("Creating ideas tailored to your profile…"):
            ai_response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=ai_prompt,
            )
        ideas = (ai_response.text or "").strip()
        if not ideas:
            st.error("Gemini returned an empty response. Please try again.")
            st.stop()
        st.markdown(ideas)
        st.caption(source_note)
        st.download_button(
            "⬇️ Download ideas as Markdown",
            data=f"# CreatorPulse AI — Content Ideas\n\n{ideas}\n\n---\n{source_note}\n",
            file_name="creatorpulse-content-ideas.md",
            mime="text/markdown",
        )
        with st.expander("📋 Copy-friendly version"):
            st.code(ideas, language=None, wrap_lines=True)
    except Exception as error:
        st.error(f"Idea generation failed. Please try again. Details: {error}")
