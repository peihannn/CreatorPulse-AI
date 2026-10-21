from __future__ import annotations

import pandas as pd
import streamlit as st

from metrics import EVENT_COLUMNS, summarize_event_log


st.set_page_config(page_title="Social Loop Studio", page_icon="🔁", layout="wide")

st.markdown(
    """
    <style>
      .block-container {max-width: 1500px; padding: 1.2rem 1.6rem 3rem;}
      [data-testid="stSidebar"] {background:#f7f9fd;}
      .brand {font-size:1.48rem;font-weight:800;color:#101c42;padding:.2rem 0 1rem;}
      .brand span {color:#2463eb;}
      .eyebrow {font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;
        color:#60708f;font-weight:700;margin-bottom:.25rem;}
      .hero {padding:1.25rem 1.5rem;border-radius:16px;
        background:linear-gradient(115deg,#10234a,#315b91 62%,#7050a2);
        color:white;margin:.5rem 0 1rem;}
      .hero h1 {color:white;margin:0 0 .3rem;font-size:2rem;}
      .hero p {color:#e8edff;margin:0;font-size:.98rem;}
      .data-note {padding:.65rem .9rem;border:1px solid #dbe5fb;background:#f4f7ff;
        border-radius:10px;color:#4b5d80;font-size:.87rem;margin:.3rem 0 .8rem;}
      .signal {padding:.9rem 1rem;border:1px solid #e4e9f2;border-radius:12px;
        margin:.45rem 0;background:white;}
      .signal-title {font-weight:700;color:#172447;margin-bottom:.22rem;}
      .signal-copy {color:#64718b;font-size:.9rem;}
      [data-testid="stMetric"] {background:#f5f7fc;padding:.85rem .95rem;border-radius:12px;
        border:1px solid #e8edf6;}
      div[data-testid="stVerticalBlockBorderWrapper"] {border-radius:13px;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand">Social Loop <span>Studio</span></div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Overview", "Data explorer"],
        label_visibility="collapsed",
        format_func=lambda item: {"Overview": "⌂  Overview", "Data explorer": "▥  Data explorer"}[item],
    )
    st.divider()
    st.caption("PRODUCT AREA")
    st.write("Video share → TikTok DM → conversation")
    st.caption("Independent portfolio concept · not affiliated with TikTok")
    with st.expander("About this demo · data & sources"):
        st.caption("Dashboard metrics and weekly trends are synthetic examples, not TikTok telemetry. External research below is contextual evidence only; it is not combined with the demo funnel.")
        st.markdown(
            "**External sharing research (directional, not representative):** a 2026 consent-based data donation study recorded 7.5M shares from 16,981 people across 83 countries through Jul 16, 2026. TikTok DMs were 90.1% of destinations, copied links 4.0%, and WhatsApp 2.5%. Participants self-selected. SMS, Facebook, and Instagram are shown as possible share options, without invented channel volumes.\n\n"
            "**Product context:** TikTok announced Shared Feed and Shared Collection in Dec. 2025. Pew's 2026 survey measures platform use, not sharing behavior. There is no public, representative dataset for country-level TikTok share destinations or recipient open-to-reply conversion. External app opens/replies are not observable here.\n\n"
            "Sources: [State of the Feed · 2026 donated TikTok data](https://wrapped.vantezzen.io/state-of-the-feed) · [Pew · 2026 social platform use](https://www.pewresearch.org/global/2026/10/01/social-media-platform-use-around-the-world/) · [TikTok · Shared Feed and Shared Collection](https://newsroom.tiktok.com/new-ways-for-friends-and-families-to-discover-share-and-connect-on-tiktok?lang=en)"
        )

top_left, top_right = st.columns([4, 1.2])
with top_left:
    st.markdown('<div class="eyebrow">SOCIAL PRODUCT · CORE INTERACTION</div>', unsafe_allow_html=True)
    page_titles = {"Overview": "Share → Conversation", "Data explorer": "Analyze an event dataset"}
    st.title(page_titles[page])
with top_right:
    st.caption("SAMPLE WINDOW")
    st.write("Apr 17–Jun 11, 2025 · synthetic sample")
st.markdown('<div class="data-note">ⓘ  SIMULATED PRODUCT DATA — the dashboard funnel below is illustrative, not TikTok telemetry. External research figures are shown separately with their source and sample limitations; they are not mixed into this funnel.</div>', unsafe_allow_html=True)
# One consistent synthetic dataset powers both dashboard views.
funnel = pd.DataFrame(
    [
        ("Eligible video impressions", "impression_id", 2_000_000, "Valid video starts"),
        ("Share sheet opened", "view_id", 222_000, "Unique eligible views with share sheet opened"),
        ("Recipient delivered", "share_recipient_id", 175_000, "Successful per-recipient deliveries"),
        ("Recipient opened", "share_recipient_id", 141_600, "Delivered recipient-video shares opened"),
        ("Recipient replied ≤24h", "share_recipient_id", 34_537, "Opened shares with a reply in 24 hours"),
        ("2+ message exchanges ≤24h", "share_recipient_id", 16_050, "Opened shares with 2+ exchanges in 24 hours"),
    ], columns=["Step", "Counting unit", "Count", "Definition"]
)
weekly = pd.DataFrame(
    [
        ("Apr 17–23", 250_000, 25_000, 19_500, 15_000, 3_300, 1_400),
        ("Apr 24–30", 250_000, 26_000, 20_000, 16_000, 3_520, 1_550),
        ("May 1–7", 250_000, 27_000, 21_000, 17_000, 3_910, 1_700),
        ("May 8–14", 250_000, 27_500, 21_500, 17_400, 4_176, 1_900),
        ("May 15–21", 250_000, 28_000, 22_000, 18_100, 4_525, 2_100),
        ("May 22–28", 250_000, 29_000, 23_000, 19_000, 4_940, 2_400),
        ("May 29–Jun 4", 250_000, 30_000, 24_500, 20_100, 5_226, 2_550),
        ("Jun 5–11", 250_000, 29_500, 23_500, 19_000, 4_940, 2_450),
    ], columns=["Week", "Eligible impressions", "Share sheets", "Sends", "Opens", "Replies ≤24h", "2+ exchanges"]
).set_index("Week")
weekly_rates = pd.DataFrame(index=weekly.index)
weekly_rates["Share-sheet open rate"] = weekly["Share sheets"] / weekly["Eligible impressions"] * 100
weekly_rates["Recipient open rate"] = weekly["Opens"] / weekly["Sends"] * 100
weekly_rates["Open → reply ≤24h"] = weekly["Replies ≤24h"] / weekly["Opens"] * 100
weekly_rates["2+ exchanges / opens"] = weekly["2+ exchanges"] / weekly["Opens"] * 100
week_starts = pd.to_datetime(["2025-04-17", "2025-04-24", "2025-05-01", "2025-05-08", "2025-05-15", "2025-05-22", "2025-05-29", "2025-06-05"])
week_labels = ["04/17", "04/24", "05/01", "05/08", "05/15", "05/22", "05/29", "06/05"]
weekly_rates.index = week_labels
destination_segments = pd.DataFrame(
    [("1:1 DM", 105_000, 87_000, 24_100, 12_200), ("Group DM", 70_000, 54_600, 10_437, 3_850)],
    columns=["Share destination", "Sends", "Opens", "Replies ≤24h", "2+ exchanges ≤24h"],
)
duration_segments = pd.DataFrame(
    [("≤20 sec", 65_000, 54_000, 14_000, 6_900), ("21–40 sec", 72_000, 58_500, 14_000, 6_500), (">40 sec", 38_000, 29_100, 6_537, 2_650)],
    columns=["Video duration", "Sends", "Opens", "Replies ≤24h", "2+ exchanges ≤24h"],
)

EVENT_CSV_TEMPLATE = """event_name,event_ts,impression_id,view_id,share_id,share_recipient_id,destination_type,video_duration_sec,country,language,experiment_id,variant
eligible_impression,2025-05-01T12:00:00Z,imp_1,,,,,18,US,en,reply_prompt_v1,control
share_sheet_open,2025-05-01T12:00:08Z,,view_1,,,,18,US,en,reply_prompt_v1,control
share_sent,2025-05-01T12:00:20Z,,,share_1,share_1_user_2,1:1,18,US,en,reply_prompt_v1,control
recipient_open,2025-05-01T12:10:00Z,,,,share_1_user_2,1:1,18,US,en,reply_prompt_v1,control
recipient_reply,2025-05-01T12:14:00Z,,,,share_1_user_2,1:1,18,US,en,reply_prompt_v1,control
conversation_2plus,2025-05-01T12:18:00Z,,,,share_1_user_2,1:1,18,US,en,reply_prompt_v1,control
"""
videos = pd.DataFrame(
    [
        ("A day in my life (3 things that helped)", "0:28", "Lifestyle", 18.4, 31.2, [12.8, 13.4, 14.2, 15.0, 15.8, 16.9, 18.0, 18.4], 1_420),
        ("POV: morning espresso with my dog", "0:32", "Lifestyle", 16.9, 28.6, [14.3, 14.7, 15.0, 15.2, 15.5, 15.7, 16.4, 16.9], 1_120),
        ("Hidden spots in Kyoto you must see", "0:26", "Travel", 14.7, 26.1, [11.8, 12.2, 12.8, 13.6, 14.0, 14.4, 14.5, 14.7], 980),
        ("5-minute noodle hack", "0:21", "Food", 13.1, 23.8, [16.3, 16.0, 15.5, 15.0, 14.6, 14.0, 13.5, 13.1], 760),
    ],
    columns=["Video", "Length", "Niche", "Latest share rate (%)", "Open → reply (%)", "Weekly share rate trend", "Shares this week"],
)
depth_trend = pd.DataFrame(
    {
        "1 reply": [60, 59, 58, 57, 56, 55, 53, 50],
        "2 replies": [21, 21, 22, 22, 22, 22, 23, 24],
        "3 replies": [12, 12, 12, 13, 13, 13, 14, 15],
        "4+ replies": [7, 8, 8, 8, 9, 10, 10, 11],
    }, index=week_labels,
)

if page == "Overview":
    st.markdown('<div class="eyebrow">EXECUTIVE OVERVIEW · VIDEO SHARE → CONVERSATION</div>', unsafe_allow_html=True)
    st.subheader("Performance at a glance")
    st.caption("Demo period: Apr 17–Jun 11, 2025 · primary comparison: most recent 28 days (May 15–Jun 11) vs. previous 28 days (Apr 17–May 14).")

    current_28 = weekly.iloc[-4:].sum(numeric_only=True)
    previous_28 = weekly.iloc[-8:-4].sum(numeric_only=True)
    all_current = weekly.sum(numeric_only=True)
    rate_definitions = {
        "Share-sheet open rate": ("Share sheets", "Eligible impressions"),
        "Recipient open rate": ("Opens", "Sends"),
        "Open → reply ≤24h": ("Replies ≤24h", "Opens"),
        "2+ exchanges / opens": ("2+ exchanges", "Opens"),
    }
    current_rates = {label: current_28[numerator] / current_28[denominator] * 100 for label, (numerator, denominator) in rate_definitions.items()}
    previous_rates = {label: previous_28[numerator] / previous_28[denominator] * 100 for label, (numerator, denominator) in rate_definitions.items()}
    period_delta = {label: current_rates[label] - previous_rates[label] for label in current_rates}
    eight_week_rates = {label: all_current[numerator] / all_current[denominator] * 100 for label, (numerator, denominator) in rate_definitions.items()}

    kpis = st.columns(3)
    for col, label in zip(kpis, ["Share-sheet open rate", "Open → reply ≤24h", "2+ exchanges / opens"]):
        change = period_delta[label]
        with col:
            numerator, denominator = rate_definitions[label]
            st.metric(label, f"{current_rates[label]:.1f}%", f"{change:+.1f} pp vs prior 28d", help=f"Current 28d: {int(current_28[numerator]):,} ÷ {int(current_28[denominator]):,}. Previous 28d: {int(previous_28[numerator]):,} ÷ {int(previous_28[denominator]):,}.")
            st.caption(f"Prior 28d: {previous_rates[label]:.1f}% · 8-week rate: {eight_week_rates[label]:.1f}% · synthetic")

    journey_rows = [
        ("1 · Eligible video impressions", int(current_28["Eligible impressions"]), "Baseline", None),
        ("2 · Share sheet opened", int(current_28["Share sheets"]), "Share-sheet open rate", "Share sheets"),
        ("3 · Recipient delivered", int(current_28["Sends"]), "Recipient delivery", "Sends"),
        ("4 · Recipient opened", int(current_28["Opens"]), "Recipient open rate", "Opens"),
        ("5 · Recipient replied ≤24h", int(current_28["Replies ≤24h"]), "Open → reply ≤24h", "Replies ≤24h"),
        ("6 · 2+ message exchanges ≤24h", int(current_28["2+ exchanges"]), "2+ exchanges / opens", "2+ exchanges"),
    ]
    journey_table = []
    for index, (label, count, rate_name, _) in enumerate(journey_rows):
        if index == 0:
            current_rate, previous_rate, delta = 100.0, 100.0, 0.0
        elif index == 2:
            current_rate, previous_rate, delta = None, None, None
        else:
            current_rate = current_rates[rate_name]
            previous_rate = previous_rates[rate_name]
            delta = period_delta[rate_name]
        direction = "↑" if delta is not None and delta > 0.05 else "↓" if delta is not None and delta < -0.05 else "→"
        journey_table.append((label, f"{count:,}", "—" if current_rate is None else f"{current_rate:.1f}%", "— · recipient-level count" if delta is None and index == 2 else "—" if delta is None else f"{delta:+.1f} pp {direction}"))

    worst_step = min((name for name in current_rates if name != "Share-sheet open rate"), key=lambda name: period_delta[name])
    worst_delta = period_delta[worst_step]
    reply_opens = int(current_28["Opens"])
    replied_opens = int(current_28["Replies ≤24h"])
    no_reply_opens = reply_opens - replied_opens
    no_reply_share = no_reply_opens / reply_opens * 100 if reply_opens else 0
    with st.container(border=True):
        st.subheader("Observed behavior · opened shares without a reply")
        st.metric("Opened · no reply ≤24h", f"{no_reply_opens:,}", help="Opened recipient-shares with no qualifying reply in the next 24 hours. This is a diagnostic count, not a success metric.")
        st.caption(f"{no_reply_share:.1f}% of opened shares · synthetic sample; indicates where replies did not occur, not why.")
    if worst_delta < 0:
        st.info(f"Separate watch item: the largest decline vs. the previous 28 days is **{worst_step}**, {previous_rates[worst_step]:.1f}% → {current_rates[worst_step]:.1f}% ({worst_delta:+.1f} pp). Investigate this step and relevant cohorts separately.")
    else:
        st.info("No recipient conversion rate declined vs. the previous 28 days in this synthetic sample. Cross-app opens/replies are not included.")
    with st.container(border=True):
        st.subheader("Share-to-conversation funnel · recent 28 days")
        journey_frame = pd.DataFrame(journey_table, columns=["Journey step", "Current 28d events", "Current 28d conversion", "Change vs prior 28d"])
        st.dataframe(journey_frame, hide_index=True, width="stretch")
        st.caption("Recent 28 days vs. the prior 28 days. Counts are events/recipient-shares, not unique people. Delivery count is not divided by share-sheet opens because those have different counting units.")

    with st.container(border=True):
        st.subheader("Segment comparison · 8-week sample")
        st.caption("Compare like-for-like rates by share destination or video length. All figures are synthetic; selecting a segment does not change the overview totals above.")
        segment_dimension = st.radio("Compare cohorts by", ["Share destination", "Video duration"], horizontal=True, key="overview_segment_dimension")
        segment_data = destination_segments if segment_dimension == "Share destination" else duration_segments
        segment_label = segment_data.columns[0]
        segment_comparison = segment_data[[segment_label, "Sends", "Opens", "Replies ≤24h", "2+ exchanges ≤24h"]].copy()
        segment_comparison["Recipient open rate"] = segment_comparison["Opens"] / segment_comparison["Sends"] * 100
        segment_comparison["Open → reply ≤24h"] = segment_comparison["Replies ≤24h"] / segment_comparison["Opens"] * 100
        segment_comparison["2+ exchanges / opens"] = segment_comparison["2+ exchanges ≤24h"] / segment_comparison["Opens"] * 100
        segment_rates = segment_comparison.set_index(segment_label)[["Recipient open rate", "Open → reply ≤24h", "2+ exchanges / opens"]].round(1)
        segment_cols = st.columns([1.25, 1])
        with segment_cols[0]:
            st.dataframe(
                segment_comparison[[segment_label, "Sends", "Opens", "Replies ≤24h", "2+ exchanges ≤24h", "Recipient open rate", "Open → reply ≤24h", "2+ exchanges / opens"]],
                hide_index=True,
                width="stretch",
                column_config={
                    "Recipient open rate": st.column_config.NumberColumn(format="%.1f%%"),
                    "Open → reply ≤24h": st.column_config.NumberColumn(format="%.1f%%"),
                    "2+ exchanges / opens": st.column_config.NumberColumn(format="%.1f%%"),
                },
            )
        with segment_cols[1]:
            st.bar_chart(segment_rates, height=300, y_label="Rate (%)")
        st.caption("Open rate = opened recipient-shares ÷ delivered recipient-shares. Reply and 2+ exchange rates use opened recipient-shares as the denominator. These are cohort comparisons, not evidence of cause.")

    chart_cols = st.columns([1.1, 1.25])
    with chart_cols[0]:
        with st.container(border=True):
            st.subheader("Conversion trend · 8 weeks")
            trend_metric = st.selectbox("Metric", list(weekly_rates.columns), key="overview_trend_metric")
            st.line_chart(weekly_rates[[trend_metric]], height=260, y_label="Rate (%)")
            first_value, last_value = weekly_rates[trend_metric].iloc[[0, -1]]
            st.markdown(f"**Eight-week movement:** {first_value:.1f}% → {last_value:.1f}% ({last_value - first_value:+.1f} pp)")
            st.caption("One metric at a time keeps the percentage scale interpretable. All rates use TikTok-side events; external recipient activity is not inferred.")
    with chart_cols[1]:
        with st.container(border=True):
            st.subheader("Reply count mix · conversations with a reply")
            st.bar_chart(depth_trend, height=260, stack=True, y_label="Share of replied conversations (%)")
            depth_delta = depth_trend["4+ replies"].iloc[-1] - depth_trend["4+ replies"].iloc[-2]
            st.markdown(f"**4+ replies:** {depth_trend['4+ replies'].iloc[-2]}% → {depth_trend['4+ replies'].iloc[-1]}% (**{depth_delta:+.0f} pp week over week**)")
            st.caption("Each bar = 100% of conversations that received at least one reply that week, split by reply count. Shares with no reply are excluded. Synthetic distribution.")

    formula_by_metric = {
        "Share-sheet open rate": "Share sheets opened ÷ eligible video impressions",
        "Recipient open rate": "Delivered recipient-shares opened ÷ recipient-shares delivered",
        "Open → reply ≤24h": "Opened recipient-shares with a reply within 24h ÷ opened recipient-shares",
        "2+ exchanges / opens": "Opened recipient-shares with 2+ exchanges within 24h ÷ opened recipient-shares",
    }
    numerator_by_metric = {
        "Share-sheet open rate": "Share sheets",
        "Recipient open rate": "Opens",
        "Open → reply ≤24h": "Replies ≤24h",
        "2+ exchanges / opens": "2+ exchanges",
    }
    denominator_by_metric = {
        "Share-sheet open rate": "Eligible impressions",
        "Recipient open rate": "Sends",
        "Open → reply ≤24h": "Opens",
        "2+ exchanges / opens": "Opens",
    }
    weekly_detail = weekly.copy()
    weekly_detail[trend_metric] = weekly_rates[trend_metric].to_numpy()
    with st.expander(f"Weekly counts & formula · {trend_metric}"):
        st.caption(f"Formula: {formula_by_metric[trend_metric]} · numerator: {numerator_by_metric[trend_metric]} · denominator: {denominator_by_metric[trend_metric]} · 8 weekly points, synthetic data.")
        st.dataframe(weekly_detail, hide_index=False, width="stretch", column_config={trend_metric: st.column_config.NumberColumn(trend_metric, format="%.1f%%")})

    with st.container(border=True):
        st.subheader("Top performing videos · share-rate heat")
        sort_by = st.selectbox("Rank videos by", ["Latest share rate (%)", "Open → reply (%)", "Shares this week"], key="video_sort")
        ordered = videos.sort_values(sort_by, ascending=False).copy()
        ordered["Latest share rate (%)"] = ordered["Latest share rate (%)"].map(lambda value: f"{value:.1f}%")
        ordered["Open → reply (%)"] = ordered["Open → reply (%)"].map(lambda value: f"{value:.1f}%")
        st.dataframe(
            ordered,
            hide_index=True,
            width="stretch",
            column_config={
                "Weekly share rate trend": st.column_config.LineChartColumn("8-week share-rate heat", y_min=0, y_max=20),
                "Shares this week": st.column_config.NumberColumn("Shares · latest week", format="%,d"),
            },
        )
        st.caption("The sparkline shows weekly share rate per eligible video view over the eight-week demo window. Video-level denominators are simulated.")

elif page == "Data explorer":
    st.markdown('<div class="eyebrow">DATA EXPLORER</div>', unsafe_allow_html=True)
    st.title("Analyze an event dataset")
    st.write("Use the Overview for the funnel and cohort comparisons. This page is for calculating the same metrics from a selected input or an uploaded event CSV.")
    st.markdown("### Input → output example")
    st.write("Choose a data source and analysis scope. The output below is calculated from that input.")
    source = st.radio("Input 0 · Data source", ["Built-in synthetic sample", "Upload event CSV"], horizontal=True)
    input_col, output_col = st.columns([1, 2], gap="large")
    is_upload = source == "Upload event CSV"
    upload_error = None
    upload_events = None
    selected_segment = None
    destination_filter = "All"
    with input_col:
        attribution_window = st.selectbox("Input · Reply window", ["24 hours after open"], key="io_window")
        if not is_upload:
            input_dimension = st.selectbox("Input · Segment by", ["Share destination", "Video duration"], key="io_dimension")
            input_data = destination_segments if input_dimension == "Share destination" else duration_segments
            segment_name_col = input_data.columns[0]
            selected_segment = st.selectbox("Input · Select segment", input_data[segment_name_col].tolist(), key="io_segment")
            selected_data = input_data.loc[input_data[segment_name_col] == selected_segment].iloc[0]
            sends = int(selected_data["Sends"])
            opens = int(selected_data["Opens"])
            replies = int(selected_data["Replies ≤24h"])
            exchanges = int(selected_data["2+ exchanges ≤24h"])
            eligible = int(funnel.loc[funnel["Step"] == "Eligible video impressions", "Count"].iloc[0])
            share_sheets = int(funnel.loc[funnel["Step"] == "Share sheet opened", "Count"].iloc[0])
            demo_scope = f"{input_dimension} = {selected_segment}; Apr 17–Jun 11"
            st.caption("Input data: built-in synthetic aggregates · Apr 17–Jun 11 · eight weeks")
        else:
            uploaded = st.file_uploader("Input · Select event CSV", type=["csv"], key="event_upload")
            st.download_button("Download CSV schema example", EVENT_CSV_TEMPLATE, "social_loop_event_schema.csv", "text/csv")
            st.caption("Required columns are defined in the schema example. One row = one event; share_sent is recorded once per recipient, and share_id links recipients from the same send action. Include follow-up events through 7 days after the final send date so open attribution is complete.")
            if uploaded is not None:
                try:
                    raw_events = pd.read_csv(uploaded)
                    missing = [column for column in EVENT_COLUMNS if column not in raw_events.columns]
                    if missing:
                        upload_error = "Missing required columns: " + ", ".join(missing)
                    else:
                        raw_events["event_ts"] = pd.to_datetime(raw_events["event_ts"], errors="coerce", utc=True)
                        if raw_events["event_ts"].isna().any():
                            upload_error = "Some event_ts values are not valid timestamps."
                        else:
                            date_min = raw_events["event_ts"].min().date()
                            date_max = raw_events["event_ts"].max().date()
                            date_range = st.date_input("Input · Date range", (date_min, date_max), min_value=date_min, max_value=date_max, key="event_dates")
                            countries = ["All"] + sorted(raw_events["country"].dropna().astype(str).unique().tolist())
                            country_filter = st.selectbox("Input · Market", countries, key="event_country")
                            languages = ["All"] + sorted(raw_events["language"].dropna().astype(str).unique().tolist())
                            language_filter = st.selectbox("Input · Language", languages, key="event_language")
                            destinations = ["All"] + sorted(raw_events["destination_type"].dropna().astype(str).unique().tolist())
                            destination_filter = st.selectbox("Input · Share destination", destinations, key="event_destination")
                            duration_filter = st.selectbox("Input · Video length", ["All", "≤20 sec", "21–40 sec", ">40 sec"], key="event_duration")
                            experiments = ["All"] + sorted(raw_events["experiment_id"].dropna().astype(str).unique().tolist())
                            experiment_filter = st.selectbox("Input · Experiment", experiments, key="event_experiment")
                            variants = ["All"] + sorted(raw_events["variant"].dropna().astype(str).unique().tolist())
                            variant_filter = st.selectbox("Input · Experiment variant", variants, key="event_variant")
                            if isinstance(date_range, tuple) and len(date_range) == 2:
                                lo = pd.Timestamp(date_range[0], tz="UTC")
                                hi = pd.Timestamp(date_range[1], tz="UTC") + pd.Timedelta(days=1)
                                upload_events = raw_events.loc[(raw_events["event_ts"] >= lo) & (raw_events["event_ts"] < hi)].copy()
                            else:
                                upload_error = "Select both a start date and an end date."
                            if country_filter != "All":
                                upload_events = upload_events.loc[upload_events["country"].astype(str) == country_filter]
                            if language_filter != "All":
                                upload_events = upload_events.loc[upload_events["language"].astype(str) == language_filter]
                            if destination_filter != "All":
                                upload_events = upload_events.loc[upload_events["destination_type"].astype(str) == destination_filter]
                            if duration_filter != "All":
                                seconds = pd.to_numeric(upload_events["video_duration_sec"], errors="coerce")
                                mask = seconds.le(20) if duration_filter == "≤20 sec" else (seconds.gt(20) & seconds.le(40) if duration_filter == "21–40 sec" else seconds.gt(40))
                                upload_events = upload_events.loc[mask]
                            if variant_filter != "All":
                                upload_events = upload_events.loc[upload_events["variant"].astype(str) == variant_filter]
                            if experiment_filter != "All":
                                upload_events = upload_events.loc[upload_events["experiment_id"].astype(str) == experiment_filter]
                            demo_scope = f"{date_range[0]}–{date_range[1]}; market={country_filter}; language={language_filter}; destination={destination_filter}; duration={duration_filter}; experiment={experiment_filter}/{variant_filter}"
                except Exception as error:
                    upload_error = f"Could not read CSV: {error}"
            if uploaded is None:
                st.info("Upload an event CSV to calculate results. Or choose the built-in synthetic sample to explore the interface.")
            elif upload_error:
                st.error(upload_error)
            elif upload_events is not None:
                calculated, upload_error = summarize_event_log(upload_events)
                if upload_error:
                    st.error(upload_error)
                else:
                    row = calculated.iloc[0].to_dict()
                    eligible = int(row.get("eligible_impression", 0))
                    share_sheets = int(row.get("share_sheet_open", 0))
                    sends = int(row.get("share_sent", 0))
                    opens = int(row.get("recipient_open", 0))
                    replies = int(row.get("recipient_reply_24h", 0))
                    exchanges = int(row.get("conversation_2plus", 0))
        if not is_upload:
            pass
        elif upload_events is None or upload_error:
            sends = opens = replies = exchanges = eligible = share_sheets = 0
            demo_scope = "CSV not yet analyzed"
        else:
            st.caption(f"Filtered input: {len(upload_events):,} event rows · {demo_scope}")
    open_rate = opens / sends * 100 if sends else 0
    reply_rate = replies / opens * 100 if opens else 0
    depth_rate = exchanges / opens * 100 if opens else 0
    destination_limited = is_upload and destination_filter != "All"
    share_rate = share_sheets / eligible * 100 if eligible and not destination_limited else None
    with output_col:
        st.markdown(f"**Output · {demo_scope} · {attribution_window}**")
        out = st.columns(5)
        out[0].metric("Eligible impressions", "N/A" if destination_limited else f"{eligible:,}", help="Not attributable to 1:1 vs. group destination; destination is chosen after share sheet opens.")
        out[1].metric("Share-sheet open rate", "N/A" if destination_limited else (f"{share_rate:.1f}%" if share_rate is not None else "0.0%"), "Not segmentable by destination" if destination_limited else f"{share_sheets:,} ÷ {eligible:,}")
        out[2].metric("Recipient open rate", f"{open_rate:.1f}%", f"{opens:,} ÷ {sends:,} recipient deliveries")
        out[3].metric("Open → reply", f"{reply_rate:.1f}%", f"{replies:,} ÷ {opens:,}")
        out[4].metric("2+ exchanges / opens", f"{depth_rate:.1f}%", f"{exchanges:,} ÷ {opens:,}")
        if not is_upload or (upload_events is not None and not upload_error):
            st.success(f"For this input, {replies:,} of {opens:,} recipient-share opens received a reply within {attribution_window.lower()}.")
    with st.expander("See exactly how the output is calculated"):
        io_formula = pd.DataFrame(
            [
                ("Input", f"{demo_scope}; window = {attribution_window}"),
                ("Output 0", f"Share-sheet open rate = {share_sheets:,} share-sheet opens ÷ {eligible:,} eligible impressions = {share_rate:.1f}%" if share_rate is not None else "Share-sheet open rate = N/A for a destination-filtered cohort; destination is only known after the share sheet opens."),
                ("Output 1", f"Recipient open rate = {opens:,} opens ÷ {sends:,} recipient deliveries = {open_rate:.1f}%"),
                ("Output 2", f"Open → reply = {replies:,} replied opens ÷ {opens:,} opens = {reply_rate:.1f}%"),
                ("Output 3", f"Conversation depth = {exchanges:,} opens with 2+ exchanges ÷ {opens:,} opens = {depth_rate:.1f}%"),
            ], columns=["Stage", "Value / formula"]
        )
        st.dataframe(io_formula, hide_index=True, width="stretch")
    st.caption("No automatic TikTok scraping is implemented. CSV mode calculates only from the uploaded, authorized event records; sample mode uses clearly labeled synthetic aggregates.")

    with st.expander("Metric definitions & minimum event schema"):
        definitions = pd.DataFrame(
            [
                ("Share-sheet open rate", "Unique view_id values with share_sheet_open ÷ unique eligible impression_id values", "Selected event-date range; IDs are counted once"),
                ("Recipient open rate", "Delivered share_recipient_id values with a valid open ÷ delivered share_recipient_id values", "Open must occur from send through 7 days after send"),
                ("Open → reply", "Valid opened share_recipient_id values with ≥1 recipient_reply ÷ valid opened share_recipient_id values", "Reply must occur within 24h after first valid open"),
                ("2+ exchanges", "Valid opened share_recipient_id values with a conversation_2plus event ÷ valid opened share_recipient_id values", "Milestone must occur within 24h after first valid open"),
            ], columns=["Metric", "Formula / counting unit", "Attribution window"],
        )
        st.dataframe(definitions, hide_index=True, width="stretch")
        schema = pd.DataFrame(
            [
                ("event_name, event_ts", "Event definition, attribution window, time ordering"),
                ("impression_id, video_id, session_id", "Eligible view and content context"),
                ("share_id, share_recipient_id", "Send action vs. per-recipient delivery/open/reply"),
                ("destination_type, recipient_cohort", "1:1 vs. group; new vs. returning, privacy-safe"),
                ("video_duration_bucket, locale", "Content and market segmentation"),
                ("experiment_id, variant", "Assignment and intent-to-treat analysis"),
            ], columns=["Fields", "Why needed"],
        )
        st.dataframe(schema, hide_index=True, width="stretch")

st.divider()
st.caption("Social Loop Studio · Portfolio case study · Independent concept · Synthetic sample data · Not affiliated with TikTok")
