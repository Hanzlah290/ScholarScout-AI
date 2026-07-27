# 🎓 ScholarScout AI

An AI-powered scholarship discovery system that continuously searches for scholarship opportunities, extracts relevant information, and presents them through a simple dashboard.

---

# Project Vision

Finding scholarships manually is time-consuming and inefficient. Scholarship opportunities are spread across university websites, government portals, scholarship websites, and social media.

ScholarScout AI aims to automate the process of discovering scholarship opportunities by continuously monitoring trusted sources, collecting relevant pages, extracting structured scholarship information using AI, validating the extracted data, and presenting verified opportunities through a simple dashboard.

The system is designed with a modular architecture so that additional scholarship sources and countries can be added in the future without changing the overall design.

The long-term vision is to build a scalable scholarship intelligence platform capable of supporting multiple countries and multiple scholarship sources.

---

# MVP (Version 1)

The first version focuses on one country and one source only.

Country:
- China

Source:
- Official Chinese University Scholarship Pages

Target User:
- Master's students
- Software Engineering students

Features:

- Collect scholarship pages from official Chinese university websites
- Discover scholarship-related pages from official Chinese university websites.
- Filter pages likely to contain scholarship information.
- Store raw pages for future processing.
- Extract structured scholarship information using AI.
- Validate extracted information.
- Prevent duplicate scholarship entries.
- Store verified scholarships in the database.
- Display scholarships through a simple dashboard.
- Store the raw pages for future processing
- Extract scholarship information using AI
- Validate and remove duplicates
- Store verified scholarships in the database
- Display scholarships on a simple dashboard
- Prevent duplicate entries

---

# Future Vision

The architecture is designed to support additional countries without major changes.

Future versions may include:

- Chinese Government Scholarship (CSC)
- Scholarship portals
- Google Search Connector
- Facebook Connector
- Telegram
- LinkedIn
- Reddit
- Multiple countries
- Email notifications
- Telegram notifications
- AI-powered scholarship ranking
- Personalized scholarship recommendations

---

# Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## AI

- OpenAI API

## Database

- PostgreSQL

(Development may use SQLite.)

## Frontend

- Next.js
- Tailwind CSS

## Automation

- APScheduler

## Web Scraping

- BeautifulSoup
- Playwright

---

# Repository Structure

```
ScholarScoutAI/

backend/
frontend/
docs/
config/
tests/

README.md
```

---

# Current Status

🚧 Project Planning

The project is currently in the architecture and documentation phase.

Current Phase

Project documentation and architecture are complete.

Implementation will begin with the backend foundation, database, and dashboard.

---

# Contributors

- Frontend Dashboard
- Database Design
- Project Architecture

Additional contributors will implement the search agents, AI extraction pipeline, and automation system.

Current Responsibilities

Frontend
- Dashboard
- API Integration

Backend
- Source Connector
- Raw Data Collector
- AI Extraction
- Validator
- Duplicate Checker
- Scheduler

---

# License

MIT License