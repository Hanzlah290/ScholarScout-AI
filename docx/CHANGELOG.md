# Changelog

All notable changes to the **ScholarScout AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to Semantic Versioning where applicable.

---

## [Unreleased]

### Added
- Integrated live backend scheduler countdown timer and pipeline status indicator badge in the frontend navigation section (`Navbar.tsx` & `StatsSection.tsx`).
- Created dynamic individual scholarship detail view page (`app/scholarships/[id]/page.tsx`) rendering eligibility criteria, degree requirements, deadlines, and AI-generated summaries.
- Implemented `ScholarshipPageFilter` pre-filtering module to evaluate raw HTML using keyword scoring and regex patterns before calling Gemini LLM routines.
- Integrated `google-generativeai` (Google Gemini API) for structured JSON metadata extraction from unstructured HTML markup and PDF attachments.
- Added automated PDF evidence extraction module (`pdf_evidence.py`, `downloader.py`) to download and parse attached university PDF announcements.
- Added repository-level deduplication checker utilizing content hashing to prevent duplicate database writes.
- Implemented 24-hour automated source discovery background job (`run_scheduled_source_discovery`) targeting Chinese higher-education portals (`.edu.cn`).
- Added FastAPI `/api/v1/scholarships/stats` endpoint returning aggregated system metrics.

### Changed
- Refactored `run_scheduled_discovery` 6-hour extraction job to automatically handle source backoff state and error counter increments upon connection failure.
- Updated Next.js application router configuration and Tailwind CSS styling to match standard visual hierarchy rules.

### Database
- Applied migration `7334f1379176_increase_scholarship_funding_field.py` to expand column length limits for funding descriptions on the `scholarships` table.

### Dependency Changes
- Upgraded Python dependencies to include `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `apscheduler`, `google-generativeai`, `httpx`, `beautifulsoup4`, and `pytest`.
- Installed Next.js 15 frontend dependencies including `react`, `tailwindcss`, `lucide-react`, and `@radix-ui` primitive packages.

---

## [1.0.0-dev] - 2026-08-28

### Added
- Initialized core repository structure with separated `backend/` (FastAPI) and `frontend/` (Next.js) directories.
- Implemented basic SQLAlchemy declarative models for `Scholarship`, `Source`, `SearchLog`, and `UserProfile`.
- Configured Uvicorn server entrypoint (`app/main.py`) with FastAPI `lifespan` manager for database initialization and APScheduler startup.
- Established basic REST API routing under `/api/v1/scholarships` and `/api/v1/sources`.
- Added initial Pytest suite for API endpoints, filter rules, and scheduler components.

---

## Database Migration History

| Migration Script | Description | Date / Version | Tables Affected |
| :--- | :--- | :--- | :--- |
| `7334f1379176_increase_scholarship_funding_field.py` | Expanded string capacity for funding text attributes | August 2026 / dev | `scholarships` |

---

## API Changes Summary

| Endpoint | Method | Change Type | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/scholarships` | `GET` | Added | Fetch paginated/filtered list of scholarships |
| `/api/v1/scholarships/stats` | `GET` | Added | Returns live statistics (open count, active sources, pipeline state) |
| `/api/v1/scholarships/{id}` | `GET` | Added | Fetch individual scholarship details |
| `/api/v1/sources` | `GET` | Added | Fetch list of active crawling sources |

---

## Current State

ScholarScout AI is currently in **Feature-Complete MVP / Active Development (v1.0.0-dev)** status. 

### Implemented Subsystems
1. **Source Discovery & Queue Management:** Discovers and validates active `.edu.cn` university portals.
2. **Filtered AI Extraction Pipeline:** Pre-filters HTML content before running Gemini LLM queries to minimize token consumption.
3. **Task Orchestration:** Embedded `APScheduler` (`AsyncIOScheduler`) running periodic 6-hour extraction and 24-hour discovery tasks.
4. **Presentation Layer:** Functional Next.js App Router application connecting to FastAPI endpoints with fallback client handling.

---

## Guidelines for Updating This Changelog

Future developers and release engineers must adhere to the following rules when updating this document:

1. **Add Under `[Unreleased]`:** Place all new features, fixes, and database updates under the `## [Unreleased]` header during active development.
2. **Categorize Changes:** Strictly group entries into `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`, `Database`, `API`, or `Breaking Changes`.
3. **Document Database Migrations:** Whenever an Alembic migration is created, add a row to the **Database Migration History** table.
4. **Document API Changes:** Update the **API Changes Summary** table whenever routes or request/response payloads are modified.
5. **Release Tagging:** When cutting a release, rename `[Unreleased]` to the release version (e.g., `## [1.1.0] - YYYY-MM-DD`) and instantiate a fresh `## [Unreleased]` section at the top.
