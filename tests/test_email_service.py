from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from app.services.email_service import (
    _latest_completed_half_day_window,
    _received_email_search_criteria,
)


class HalfDayReceivedEmailWindowTests(unittest.TestCase):
    def test_midnight_run_fetches_the_previous_afternoon(self) -> None:
        now = datetime(2026, 6, 24, 0, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

        start, end = _latest_completed_half_day_window(now)

        self.assertEqual(
            (start, end),
            (
                datetime(2026, 6, 23, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
                datetime(2026, 6, 24, 0, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
            ),
        )

    def test_noon_run_fetches_the_same_day_morning(self) -> None:
        now = datetime(2026, 6, 24, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

        start, end = _latest_completed_half_day_window(now)
        criteria = _received_email_search_criteria(start, end)

        self.assertEqual(
            (start, end),
            (
                datetime(2026, 6, 24, 0, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
                datetime(2026, 6, 24, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata")),
            ),
        )
        self.assertEqual(
            criteria,
            ("ALL", "SINCE", "24-Jun-2026", "BEFORE", "25-Jun-2026"),
        )
