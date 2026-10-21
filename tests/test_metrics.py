import unittest

import pandas as pd

from metrics import EVENT_COLUMNS, summarize_event_log


def make_row(event_name, timestamp, recipient_id=None, impression_id=None, view_id=None):
    row = {column: None for column in EVENT_COLUMNS}
    row.update(
        event_name=event_name,
        event_ts=timestamp,
        impression_id=impression_id,
        view_id=view_id,
        share_recipient_id=recipient_id,
    )
    return row


class SummarizeEventLogTests(unittest.TestCase):
    def test_applies_send_open_and_24_hour_attribution_windows(self):
        rows = [
            make_row("eligible_impression", "2025-01-01T00:00:00Z", impression_id="imp-1"),
            make_row("share_sheet_open", "2025-01-01T00:01:00Z", view_id="view-1"),
            make_row("share_sent", "2025-01-01T00:00:00Z", recipient_id="valid"),
            make_row("recipient_open", "2025-01-02T00:00:00Z", recipient_id="valid"),
            make_row("recipient_reply", "2025-01-03T00:00:00Z", recipient_id="valid"),
            make_row("conversation_2plus", "2025-01-02T12:00:00Z", recipient_id="valid"),
            make_row("share_sent", "2025-01-01T00:00:00Z", recipient_id="late-open"),
            make_row("recipient_open", "2025-01-08T00:00:01Z", recipient_id="late-open"),
            make_row("recipient_reply", "2025-01-08T01:00:00Z", recipient_id="late-open"),
            make_row("conversation_2plus", "2025-01-08T02:00:00Z", recipient_id="late-open"),
            make_row("share_sent", "2025-01-01T00:00:00Z", recipient_id="late-reply"),
            make_row("recipient_open", "2025-01-01T01:00:00Z", recipient_id="late-reply"),
            make_row("recipient_reply", "2025-01-02T01:00:01Z", recipient_id="late-reply"),
            make_row("conversation_2plus", "2025-01-02T01:00:01Z", recipient_id="late-reply"),
            make_row("recipient_open", "2025-01-01T02:00:00Z", recipient_id="orphan-open"),
        ]

        result, error = summarize_event_log(pd.DataFrame(rows))

        self.assertIsNone(error)
        self.assertEqual(result.loc[0, "share_sent"], 3)
        self.assertEqual(result.loc[0, "recipient_open"], 2)
        self.assertEqual(result.loc[0, "recipient_reply_24h"], 1)
        self.assertEqual(result.loc[0, "conversation_2plus"], 1)

    def test_rejects_missing_event_identifier(self):
        rows = [make_row("recipient_open", "2025-01-01T00:00:00Z")]

        result, error = summarize_event_log(pd.DataFrame(rows))

        self.assertTrue(result.empty)
        self.assertIn("share_recipient_id", error)

    def test_rejects_unknown_events(self):
        rows = [make_row("unrecognized_event", "2025-01-01T00:00:00Z")]

        result, error = summarize_event_log(pd.DataFrame(rows))

        self.assertTrue(result.empty)
        self.assertIn("Unknown event_name", error)


if __name__ == "__main__":
    unittest.main()
