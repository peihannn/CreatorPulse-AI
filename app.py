import streamlit as st
import pandas as pd#
from google import genai

st.set_page_config(
    page_title="CreatorPulse AI",
    page_icon="🎬",
    layout="wide"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.title("🎬 CreatorPulse AI")

st.subheader(
    "Turn Social Trends into Original Content Ideas"
)

st.write(
    "An AI-powered creative copilot helping content creators "
    "discover relevant trends and develop personalized video ideas."
)

st.divider()

st.header("👤 Creator Profile")

creator_name = st.text_input(
    "Creator Name",
    placeholder="e.g. NYC Student Creator"
)

content_niche = st.selectbox(
    "Content Niche",
    [
        "Lifestyle",
        "Education",
        "Technology",
        "Fashion",
        "Food",
        "Travel",
        "Entertainment"
    ]
)

target_audience = st.text_input(
    "Target Audience",
    placeholder="e.g. International students aged 18–24"
)

content_style = st.selectbox(
    "Content Style",
    [
        "Authentic",
        "Funny",
        "Educational",
        "Inspirational",
        "Storytelling"
    ]
)

st.divider()

trends_df = pd.read_csv("trends.csv")

with st.expander("📊 View Simulated Trend Dataset"):
    st.caption(
        "These records are simulated examples for product testing, "
        "not real-time social media trends."
    )
    st.dataframe(
        trends_df,
        width="stretch"
    )

if st.button("🔍 Analyze Trends", type="primary"):
    if not creator_name.strip() or not target_audience.strip():
        st.warning(
            "Please enter both Creator Name and Target Audience."
        )
        st.stop()

    st.success("Creator profile created successfully!")

    st.write("### Your Creator Profile")

    st.write("**Name:**", creator_name)
    st.write("**Content Niche:**", content_niche)
    st.write("**Target Audience:**", target_audience)
    st.write("**Content Style:**", content_style)

    audience_query = target_audience.strip().lower()

    audience_matches = trends_df["audience"].str.lower().apply(
        lambda audience: (
            audience in audience_query
            or audience_query in audience
        )
    )

    matched_trends = trends_df[
        (trends_df["niche"] == content_niche)
        & (trends_df["style"] == content_style)
        & audience_matches
    ].sort_values(
        by="popularity_score",
        ascending=False
    )

    st.subheader("🎯 Matching Simulated Trends")

    if matched_trends.empty:
        st.warning("No matching simulated trends were found.")
    else:
        st.dataframe(
            matched_trends,
            width="stretch",
            hide_index=True
        )

        top_trend = matched_trends.iloc[0]

        ai_prompt = f"""
You are a creative strategist for short-form video.

Use the following simulated trend only as creative inspiration.
Do not describe it as a real-time or verified social media trend.

Creator name: {creator_name}
Content niche: {content_niche}
Target audience: {target_audience}
Content style: {content_style}

Simulated trend: {top_trend["trend_name"]}
Trend description: {top_trend["description"]}
Simulated popularity score: {top_trend["popularity_score"]}

Generate exactly 3 original short-form video ideas.

For each idea, include:
1. Title
2. Opening hook
3. Core concept
4. Three-beat outline
5. Call to action

Keep the recommendations concise and personalized.
"""

        st.subheader("✨ AI-Generated Content Ideas")

        try:
            with st.spinner("Gemini is developing original ideas..."):
                ai_response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=ai_prompt
                )

            st.markdown(ai_response.text)

        except Exception as error:
            st.error(f"AI idea generation failed: {error}")