# Social Loop Studio

Social Loop Studio is an independent product concept about what happens after someone shares a TikTok video: does the recipient open it, reply, and continue the conversation?

The demo turns that journey into a small product analytics workflow. It is designed to help a product team spot where interaction drops off and compare outcomes across sharing destinations and video-length segments.

> **Data note:** Dashboard figures are synthetic examples, not TikTok telemetry. The app does not scrape TikTok or connect to TikTok APIs. CSV analysis only uses event records supplied by the user. This is an independent portfolio concept and is not affiliated with TikTok.

## What you can explore

- **Overview:** a share-to-conversation funnel, current 28 days versus the previous 28 days, an eight-week trend, segment comparisons, and example video-level metrics.
- **Data explorer:** select a sample segment or upload an event CSV to calculate the defined rates from the input data.
- **Metric definitions:** see the counting units and attribution windows used by the demo.

The synthetic dashboard sample covers Apr 17–Jun 11, 2025. Its values are illustrative and should not be interpreted as current or representative TikTok behavior.

## Run locally

Requires Python 3.12 or later.

```bash
git clone https://github.com/peihannn/CreatorPulse-AI.git
cd CreatorPulse-AI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Uploading event data

In **Data explorer**, choose **Upload event CSV** and download the example schema from the app. Each row represents an event. The file needs the columns shown in that example, including event name and timestamp, the relevant event IDs, destination and video duration, market/language, and experiment/variant fields.

The app calculates rates only from the uploaded rows. In particular, an open-to-reply rate uses opened recipient shares as its denominator and counts replies within 24 hours of the first open. Do not upload personal message content or data you are not authorized to use.

## Project files

- `app.py` — Streamlit application and demo calculations
- `trends.csv` — sample content dataset retained from the initial CreatorPulse AI MVP
- `requirements.txt` — pinned Python dependencies

## Scope

This is a portfolio demo, not a production analytics integration. It does not fetch live data, send messages, assign experiment cohorts, or measure the impact of a product change. Those capabilities would require approved event instrumentation, privacy review, and access to authorized data.
