import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import os
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from app.services.email_service import fetch_received_emails
from app.schemas import TicketPayload
from app.services.email_categorization import categorize_email

load_dotenv()

logger = logging.getLogger(__name__)

SCHEDULE_MINUTE = int(os.getenv("EMAIL_CLASSIFICATION_MINUTE", "0"))
SCHEDULE_TIMEZONE = os.getenv("EMAIL_CLASSIFICATION_TIMEZONE", "Asia/Kolkata")


def _to_ticket(email_data: dict[str, str]) -> TicketPayload:
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")

    return TicketPayload(
        client_email=email_data.get("from", "unknown"),
        category=categorize_email(subject, body),
        raw_transcript=f"Subject: {subject}\n\n{body}",
    )


async def collect_categorized_recent_emails() -> list[TicketPayload]:
    """Fetch the latest completed 12-hour mail window off the event loop."""

    raw_emails = await asyncio.to_thread(fetch_received_emails)
    return [_to_ticket(email_data) for email_data in raw_emails]


async def run_twice_daily_email_categorization() -> None:
    """Process the latest completed 12-hour window and retain its result."""

    try:
        tickets = await collect_categorized_recent_emails()
        app.state.latest_scheduled_tickets = tickets
        logger.info("Categorized %s email(s) in the scheduled 12-hour window.", len(tickets))
    except Exception:
        logger.exception("Twice-daily email categorization job failed.")


@asynccontextmanager
async def lifespan(application: FastAPI):
    scheduler = AsyncIOScheduler(timezone=ZoneInfo(SCHEDULE_TIMEZONE))
    scheduler.add_job(
        run_twice_daily_email_categorization,
        trigger=CronTrigger(
            hour="0,12",
            minute=SCHEDULE_MINUTE,
            timezone=SCHEDULE_TIMEZONE,
        ),
        id="twice-daily-email-categorization",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=12 * 60 * 60,
    )
    application.state.latest_scheduled_tickets = []
    application.state.email_scheduler = scheduler
    scheduler.start()
    logger.info(
        "Email categorization scheduled daily at 00:%02d and 12:%02d %s.",
        SCHEDULE_MINUTE,
        SCHEDULE_MINUTE,
        SCHEDULE_TIMEZONE,
    )

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="AI Email Ticketing - Client Plane", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Client Plane API is running."}


@app.get("/fetch-emails")
async def api_fetch_emails():
    """
    Fetches all emails from the latest completed 12-hour window and returns
    keyword-categorized ticket payloads.
    """
    try:
        tickets = await collect_categorized_recent_emails()

        return {
            "status": "success",
            "count": len(tickets),
            "data": [ticket.model_dump(mode="json") for ticket in tickets]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
