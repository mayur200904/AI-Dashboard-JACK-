# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Agents.md**: Created to guide AI tools with rules on maintaining MVP focus and simplicity.
- **Spec.md**: Established initial functional specifications, technology stack, and architecture goals.
- **FastAPI Application (`app/main.py`)**: Added an entry point and background task for twice-daily email retrieval and categorization.
- **Data Schemas (`app/schemas.py`)**: Implemented `TicketPayload` via Pydantic to format raw emails into structured tickets with attributes like `category`, `priority`, and `sentiment`.
- **Services setup**: Scaffolded structure for `email_service` (fetching) and `email_categorization` (AI categorization logic).
- **Testing environment**: Initialized a `tests` directory with boilerplate test structures for ticket mapping and email services.

### Changed
- Project configuration initialized via `requirements.txt`.
