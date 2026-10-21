"""Metric definitions and event-log calculations for Social Loop Studio."""

from __future__ import annotations

import pandas as pd


EVENT_COLUMNS = [
    "event_name", "event_ts", "impression_id", "view_id", "share_id",
    "share_recipient_id", "destination_type", "video_duration_sec",
    "country", "language", "experiment_id", "variant",
]

ALLOWED_EVENTS = {
    "eligible_impression", "share_sheet_open", "share_sent", "recipient_open",
    "recipient_reply", "conversation_2plus",
}

SEND_TO_OPEN_WINDOW = pd.Timedelta(days=7)
OPEN_TO_REPLY_WINDOW = pd.Timedelta(hours=24)


def summarize_event_log(events: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """Calculate unique event counts and attributed recipient outcomes.

    Recipient opens count only when they occur from send time through 7 days
    after send. Replies and 2+ exchange milestones count only from the first
    valid recipient open through the following 24 hours.
    """
    missing = [column for column in EVENT_COLUMNS if column not in events.columns]
    if missing:
        return pd.DataFrame(), "Missing required columns: " + ", ".join(missing)

    frame = events.copy()
    frame["event_ts"] = pd.to_datetime(frame["event_ts"], errors="coerce", utc=True)
    if frame["event_ts"].isna().any():
        return pd.DataFrame(), "Some event_ts values could not be parsed as dates/times."
    if frame["event_name"].isna().any():
        return pd.DataFrame(), "Some event_name values are empty."

    unknown = sorted(set(frame["event_name"].astype(str)) - ALLOWED_EVENTS)
    if unknown:
        return pd.DataFrame(), "Unknown event_name value(s): " + ", ".join(unknown)

    id_by_event = {
        "eligible_impression": "impression_id",
        "share_sheet_open": "view_id",
        "share_sent": "share_recipient_id",
        "recipient_open": "share_recipient_id",
        "recipient_reply": "share_recipient_id",
        "conversation_2plus": "share_recipient_id",
    }
    for event_name, id_column in id_by_event.items():
        missing_ids = frame.loc[frame["event_name"] == event_name, id_column].isna()
        if missing_ids.any():
            return pd.DataFrame(), f"{event_name} rows require a non-empty {id_column}."

    counts = {
        event_name: int(frame.loc[frame["event_name"] == event_name, id_column].nunique())
        for event_name, id_column in id_by_event.items()
    }

    sends = frame.loc[frame["event_name"] == "share_sent", ["share_recipient_id", "event_ts"]]
    first_send = sends.groupby("share_recipient_id")["event_ts"].min()
    opens = frame.loc[frame["event_name"] == "recipient_open", ["share_recipient_id", "event_ts"]]
    opens = opens.join(first_send.rename("first_send"), on="share_recipient_id")
    valid_opens = opens.loc[
        opens["first_send"].notna()
        & (opens["event_ts"] >= opens["first_send"])
        & (opens["event_ts"] <= opens["first_send"] + SEND_TO_OPEN_WINDOW)
    ]
    counts["recipient_open"] = int(valid_opens["share_recipient_id"].nunique())
    first_open = valid_opens.groupby("share_recipient_id")["event_ts"].min()

    for event_name, result_name in (
        ("recipient_reply", "recipient_reply_24h"),
        ("conversation_2plus", "conversation_2plus"),
    ):
        outcomes = frame.loc[frame["event_name"] == event_name, ["share_recipient_id", "event_ts"]]
        outcomes = outcomes.join(first_open.rename("first_open"), on="share_recipient_id")
        attributed = outcomes.loc[
            outcomes["first_open"].notna()
            & (outcomes["event_ts"] >= outcomes["first_open"])
            & (outcomes["event_ts"] <= outcomes["first_open"] + OPEN_TO_REPLY_WINDOW)
        ]
        counts[result_name] = int(attributed["share_recipient_id"].nunique())

    result = pd.DataFrame([counts])
    return result, None
