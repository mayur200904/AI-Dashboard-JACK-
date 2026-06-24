import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime, time, timedelta
import re
from zoneinfo import ZoneInfo


def _classification_timezone() -> ZoneInfo:
    return ZoneInfo(os.getenv("EMAIL_CLASSIFICATION_TIMEZONE", "Asia/Kolkata"))


def _latest_completed_half_day_window(
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return the most recently completed non-overlapping 12-hour window."""

    if now is None:
        now = datetime.now(_classification_timezone())
    elif now.tzinfo is None:
        now = now.replace(tzinfo=_classification_timezone())
    else:
        now = now.astimezone(_classification_timezone())

    midnight = datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
    noon = midnight + timedelta(hours=12)

    if now < noon:
        return midnight - timedelta(hours=12), midnight
    return midnight, noon


def _received_email_search_criteria(
    start: datetime, end: datetime,
) -> tuple[str, ...]:
    """Build the broad IMAP date search used before exact timestamp filtering."""

    before_date = end.date() if end.time() == time.min else end.date() + timedelta(days=1)
    return (
        "ALL",
        "SINCE",
        start.strftime("%d-%b-%Y"),
        "BEFORE",
        before_date.strftime("%d-%b-%Y"),
    )


def _received_at(response_metadata: bytes, timezone: ZoneInfo) -> datetime | None:
    """Return the IMAP INTERNALDATE from a FETCH response in the local timezone."""

    match = re.search(rb'INTERNALDATE "([^"]+)"', response_metadata)
    if match is None:
        return None

    internal_date = datetime.strptime(
        match.group(1).decode("ascii"), "%d-%b-%Y %H:%M:%S %z"
    )
    return internal_date.astimezone(timezone)


def fetch_received_emails():
    """
    Connects to Gmail via IMAP using an App Password.
    Fetches all emails received during the most recently completed 12-hour
    window and returns a list of dictionaries with basic email data.

    IMAP's date search narrows the candidate set efficiently. Each message is
    then checked against its INTERNALDATE so the window is exact at noon and
    midnight in EMAIL_CLASSIFICATION_TIMEZONE.
    """
    EMAIL_ACCOUNT = os.getenv("GMAIL_ACCOUNT")
    APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

    if not EMAIL_ACCOUNT or not APP_PASSWORD:
        raise ValueError("Gmail credentials not set in environment.")

    # Connect to the server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    
    # Select the mailbox you want to check
    mail.select("inbox")
    
    timezone = _classification_timezone()
    start, end = _latest_completed_half_day_window()
    status, messages = mail.search(None, *_received_email_search_criteria(start, end))
    emails_data = []
    
    if status == "OK":
        for num in messages[0].split():
            # fetch the email message by ID
            res, msg = mail.fetch(num, "(RFC822 INTERNALDATE)")
            for response_part in msg:
                if isinstance(response_part, tuple):
                    received_at = _received_at(response_part[0], timezone)
                    if received_at is None or not start <= received_at < end:
                        continue

                    msg_data = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject_header = decode_header(msg_data["Subject"])[0]
                    subject, encoding = subject_header
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors='ignore')
                        
                    # Decode Sender
                    from_str = msg_data.get("From")
                    from_header = decode_header(from_str)[0] if from_str else (b"", None)
                    from_email, encoding = from_header
                    if isinstance(from_email, bytes):
                        from_email = from_email.decode(encoding if encoding else "utf-8", errors='ignore')
                        
                    # Extract Body
                    body = ""
                    if msg_data.is_multipart():
                        for part in msg_data.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                break
                    else:
                        body = msg_data.get_payload(decode=True).decode(errors='ignore')
                        
                    emails_data.append({
                        "id": num.decode('utf-8'),
                        "subject": subject,
                        "from": from_email,
                        "body": body
                    })

    mail.close()
    mail.logout()
    return emails_data
