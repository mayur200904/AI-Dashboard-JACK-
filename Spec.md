# Project Specification (Spec.md)

## Overview
The **IKF Dashboard** is an MVP application designed to act as an AI-powered Email Ticketing System. It automates the retrieval of emails and categorizes them into actionable tickets.

## Core Features
1. **Email Ingestion:** 
   - Periodically fetches the latest received emails.
   - Runs as a background task (twice daily) using `APScheduler`.

2. **Email Categorization & Processing:**
   - Extracts `subject` and `body`.
   - Categorizes the email into predefined categories (e.g., Enquiry, Escalation, Support).
   - Evaluates sentiment, priority, and flags if human intervention is required.

3. **Data Structure (TicketSchema):**
   - **Fields Include:** `ticket_id`, `source_channel`, `client_email`, `category`, `priority`, `sentiment`, `ai_summary`, `raw_transcript`, `created_at`, `kb_articles_used`, `requires_human`.

## Tech Stack
- **Framework:** FastAPI (Python 3.11)
- **Task Scheduling:** APScheduler (async)
- **Data Validation:** Pydantic
- **Environment:** `python-dotenv` for configuration

## Architecture Goals
- Provide a simple MVP that correctly identifies and categorizes incoming emails.
- Expose the processed tickets (currently kept in memory/state) for downstream usage or review.
