# Project Scope

## Project Goal

ScholarScout AI is an automation system designed to continuously search for scholarship opportunities in China.

The primary objective is to reduce the amount of manual work required to discover scholarships by automatically monitoring trusted sources, identifying scholarship-related pages, collecting raw content, extracting structured scholarship information using AI, validating the extracted data, storing verified scholarship records in a database, and presenting them through a simple dashboard.

The project is designed to be scalable so that additional countries and scholarship sources can be added in the future without changing the overall architecture.

---

# Version 1 (MVP)

The first version intentionally has a very small scope.

---

# Success Criteria (Version 1)

Version 1 will be considered complete when the system can:

- Monitor at least one official Chinese university website.
- Identify scholarship-related pages.
- Store raw pages for processing.
- Extract scholarship information using AI.
- Validate the extracted information.
- Prevent duplicate scholarship entries.
- Store verified scholarship data in the database.
- Display the stored scholarships in the dashboard.

## Country

China

## Scholarship Source

Official Chinese university scholarship pages only.

## Target Degree

Master's

## Target Field

Software Engineering

---

# Functional Requirements

The system must:

- Visit official Chinese university websites.
- Discover pages likely to contain scholarship information.
- Collect and store raw scholarship-related pages.
- Extract structured scholarship information using AI.
- Validate extracted information.
- Prevent duplicate scholarship entries.
- Store verified scholarship information in the database.
- Display scholarships on a simple dashboard.
- Allow viewing scholarship details.



---

# Non-Functional Requirements

- Modular architecture.
- Independent modules with clearly defined responsibilities.
- Easily extendable to additional countries.
- Easily extendable to additional scholarship sources.
- Reliable and easy to maintain.
- Minimal frontend; functionality is prioritized over appearance.

---

# Out of Scope (Version 1)

The following features are intentionally excluded:

- CSC scholarships
- Facebook Connector
- Google Search Connector
- Telegram Connector
- LinkedIn
- Multiple countries
- Email notifications
- AI recommendation engine
- User authentication
- Multiple users
- Mobile application

---

# Future Expansion

Future versions may support:

- Additional university source connectors
- CSC connector
- Google Search connector
- Facebook connector
- Telegram connector
- Additional countries
- Personalized scholarship matching
- Automatic notifications
- Daily scholarship reports
- AI-generated summaries
- Additional scholarship sources