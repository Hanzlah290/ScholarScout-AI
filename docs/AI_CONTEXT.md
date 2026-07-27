# AI Context

## Project Summary

Project Name:

ScholarScout AI

Purpose:

Automatically discover scholarship opportunities from official Chinese university websites, extract structured scholarship information using AI, validate the results, store verified scholarships, and display them in a dashboard.

Version 1 focuses only on official Chinese university websites.

---

# Technology Stack

Frontend

- Next.js
- TypeScript
- Tailwind CSS

Backend

- FastAPI
- Python

Database

- PostgreSQL
- SQLAlchemy
- Alembic

AI

- OpenAI API

Web Scraping

- Playwright
- BeautifulSoup

Scheduler

- APScheduler

---

# System Architecture

```
Scheduler
    │
    ▼
Source Connector
    │
    ▼
Keyword & URL Filter
    │
    ▼
Raw Data Collector
    │
    ▼
AI Extraction Module
    │
    ▼
Validator
    │
    ▼
Duplicate Checker
    │
    ▼
Database
    │
    ▼
Backend API
    │
    ▼
Dashboard
```

---

# Module Responsibilities

Scheduler

- Starts the pipeline.

Source Connector

- Visits configured websites.
- Downloads webpages.

Keyword & URL Filter

- Removes irrelevant pages.

Raw Data Collector

- Stores downloaded webpages.

AI Extraction Module

- Extracts scholarship information.

Validator

- Validates extracted data.

Duplicate Checker

- Prevents duplicate records.

Database

- Stores verified scholarships.

Backend API

- Serves scholarship data.

Dashboard

- Displays scholarships.

---

# Database

Main tables:

- Scholarships
- Sources
- Search Logs
- User Profile

Only verified scholarship information is stored in the database.

---

# API

Version 1 supports:

GET /scholarships

GET /scholarships/{id}

GET /health

The frontend is read-only.

---

# Development Rules

Always follow the documented architecture.

Never merge module responsibilities.

Never bypass the Validator.

Never allow the frontend to access the database directly.

Keep all modules independent.

Write modular, maintainable code.

Follow the project folder structure.

Use the technology stack defined in TECH_STACK.md.

---

# Version 1 Scope

Support:

- China
- Official university websites
- Master's scholarships
- Software Engineering

Do NOT implement:

- CSC
- Facebook
- Telegram
- Google Search
- Multiple countries
- Notifications
- Authentication
- Multiple users

These features belong to future versions only.