"""Keyword-based email categorization.

This module intentionally keeps the categorization boundary small so a future
AI-based classifier can replace ``categorize_email`` without changing the
scheduler or API contract.
"""

from enum import Enum
import re


class EmailCategory(str, Enum):
    ENQUIRY = "enquiry"
    ESCALATION = "escalation"
    SUPPORT = "support"


# More urgent language takes precedence when an email contains terms from more
# than one category, for example "urgent help needed".
CATEGORY_KEYWORDS: dict[EmailCategory, tuple[str, ...]] = {
    EmailCategory.ESCALATION: (
        "escalate",
        "escalation",
        "urgent",
        "critical",
        "complaint",
        "unresolved",
        "frustrated",
        "disappointed",
        "poor service",
        "not acceptable",
        "legal action",
        "manager",
    ),
    EmailCategory.SUPPORT: (
        "help",
        "support",
        "issue",
        "problem",
        "error",
        "failed",
        "failure",
        "not working",
        "unable to",
        "cannot",
        "can't",
        "login",
        "password",
        "bug",
        "troubleshoot",
    ),
    EmailCategory.ENQUIRY: (
        "enquiry",
        "inquiry",
        "information",
        "pricing",
        "price",
        "quote",
        "quotation",
        "demo",
        "availability",
        "interested in",
        "product details",
        "service details",
        "learn more",
    ),
}


def categorize_email(subject: str, body: str) -> EmailCategory:
    """Return the category that best matches an email's subject and body.

    Emails without a matching keyword are treated as enquiries. This gives the
    operations team a predictable queue while the AI classifier is not in use.
    """

    content = f"{subject}\n{body}".casefold()

    for category in (
        EmailCategory.ESCALATION,
        EmailCategory.SUPPORT,
        EmailCategory.ENQUIRY,
    ):
        if any(_contains_keyword(content, keyword) for keyword in CATEGORY_KEYWORDS[category]):
            return category

    return EmailCategory.ENQUIRY


def _contains_keyword(content: str, keyword: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(keyword.casefold())}(?!\w)", content) is not None
