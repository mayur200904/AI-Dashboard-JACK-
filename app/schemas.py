from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import UUID, uuid4

from app.services.email_categorization import EmailCategory


class TicketPayload(BaseModel):
    ticket_id: UUID = Field(default_factory=uuid4)
    source_channel: str = Field(description="email | whatsapp | chat | voice", default="email")
    client_email: str
    category: EmailCategory = Field(
        description="enquiry | escalation | support",
        default=EmailCategory.ENQUIRY,
    )
    priority: int = Field(ge=1, le=5, default=3)
    sentiment: str = Field(description="positive | neutral | negative | hostile", default="neutral")
    ai_summary: str = Field(description="Optional ticket summary", default="")
    raw_transcript: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    kb_articles_used: List[str] = Field(default_factory=list)
    requires_human: bool = Field(default=False)
