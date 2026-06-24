import unittest

from app.main import _to_ticket
from app.schemas import TicketPayload
from app.services.email_categorization import EmailCategory


class TicketMappingTests(unittest.TestCase):
    def test_keyword_categorization_creates_a_structured_ticket_payload(self) -> None:
        ticket = _to_ticket(
            {
                "from": "client@example.com",
                "subject": "Unable to login",
                "body": "My password reset has failed.",
            }
        )

        self.assertIsInstance(ticket, TicketPayload)
        self.assertEqual(ticket.category, EmailCategory.SUPPORT)
        self.assertEqual(ticket.client_email, "client@example.com")
        self.assertEqual(
            ticket.raw_transcript,
            "Subject: Unable to login\n\nMy password reset has failed.",
        )

