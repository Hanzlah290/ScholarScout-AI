# Contribution & Development Guidelines — ScholarScout AI

This document establishes engineering standards, development workflows, testing requirements, and safe code-modification practices for maintaining and extending **ScholarScout AI**.

---

## 1. Introduction

### Project Overview
ScholarScout AI is an automated ETL pipeline, AI-powered extraction engine, and web dashboard designed to crawl, process, and display Chinese university scholarship announcements (`.edu.cn`).

### Audience & Purpose
This guide is intended for core maintainers, contributors, and full-stack developers. It outlines the conventions required to safely modify backend APIs, AI extraction prompts, page pre-filters, database schemas, and Next.js frontend components.

---

## 2. Before You Start

### Required Knowledge
* **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic, APScheduler, Pytest.
* **Frontend:** TypeScript, Next.js (App Router), Tailwind CSS, React Hooks (`useState`, `useEffect`).
* **Services:** PostgreSQL, Google Gemini API (`google-generativeai`).

### Required Software
* Python 3.11+
* Node.js v18+ & npm/pnpm
* PostgreSQL v14+ (or a remote database instance like Supabase)
* Git

---

## 3. Development Environment

Refer to [`README.md`](./README.md) for full installation steps.

### Environment Setup Summary
1. **Backend Configuration (`backend/.env`):**
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/scholarscout
   GEMINI_API_KEY=your_gemini_api_key
   PYTHONPATH=.
   ```
2. **Frontend Configuration (`frontend/.env.local`):**
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   ```

---

## 4. Repository Structure

| Path | Description |
| :--- | :--- |
| **`backend/app/api/routes/`** | FastAPI endpoints (`scholarships.py`, `sources.py`). |
| **`backend/app/models/`** | SQLAlchemy database models (`scholarship.py`, `source.py`). |
| **`backend/app/schemas/`** | Pydantic request and response schemas (`api.py`, `pipeline.py`). |
| **`backend/app/services/`** | Core business logic (automation, pre-filtering, Gemini extraction, scheduler). |
| **`backend/migrations/`** | Alembic database migration scripts. |
| **`backend/tests/`** | Pytest test suite modules. |
| **`frontend/app/`** | Next.js App Router dynamic routes and layouts. |
| **`frontend/components/`** | Modular UI components (`DashboardClient`, `Navbar`, `ScholarshipCard`). |

---

## 5. Development Workflow

```text
1. Select Task / Issue
     ↓
2. Checkout Development Branch (`develop` or `feature/*`)
     ↓
3. Make Database / Backend / Frontend Modifications
     ↓
4. Execute Local Unit & Component Tests (`pytest`)
     ↓
5. Perform Integration Testing (FastAPI + Next.js UI)
     ↓
6. Review Code & Ensure Secrets Are Isolated
     ↓
7. Commit and Push to Remote Repository
```

---

## 6. Branching Strategy

### Existing Project Practice
The repository currently uses a primary branch structure featuring:
* **`main` / `master`:** Production-ready release code.
* **`develop`:** Primary integration branch for completed features.
* **`feature/scholarship-discovery-pipeline`:** Active feature branches for specialized modules.

### Recommended Branching Practice
* **Feature Branches:** `feature/feature-name` (e.g., `feature/user-auth`)
* **Bug Fixes:** `fix/bug-description` (e.g., `fix/pdf-timeout`)

---

## 7. Commit Guidelines

### Existing Project Practice
Commits follow standard descriptive prefixes (e.g., `feat: integrate live scheduler status`, `pushing everything to develop`).

### Recommended Conventional Commits Standard
* `feat:` A new feature addition.
* `fix:` A bug fix.
* `docs:` Documentation changes only.
* `refactor:` Code change that neither fixes a bug nor adds a feature.
* `test:` Adding missing tests or updating existing tests.

---

## 8. Code Style

### Backend (Python)
* Follow **PEP 8** standards.
* Use explicit type hints for function signatures and API schemas.
* Keep asynchronous functions explicitly annotated with `async def` where I/O operations occur.

### Frontend (TypeScript / React)
* Use functional React components with standard React Hooks.
* Enforce strict type safety using TypeScript interfaces defined in `types/scholarship.ts`.
* Styling must strictly use Tailwind utility classes.

---

## 9. Frontend Development Rules

* **State Hydration:** Client interactive state must reside inside client components (`DashboardClient.tsx`).
* **API Isolation:** Do not call `fetch` directly inside components; use methods defined in `services/scholarshipService.ts`.
* **Fallback Safety:** Maintain fallback data structures in case the live backend service is unreachable during development.

---

## 10. Backend Development Rules

* **Scoping Sessions:** Always use FastAPI dependency injection `get_db` to acquire database sessions. Do not open global un-managed DB sessions in API controllers.
* **Pre-Filtering:** Any new crawler endpoint must pass raw HTML through `ScholarshipPageFilter` before invoking the Gemini API to prevent unnecessary token consumption.

---

## 11. Database Change Rules

When changing or extending SQLAlchemy database models (`backend/app/models/`):

```text
Modify Model File (e.g., backend/app/models/scholarship.py)
     ↓
Generate Migration: alembic revision --autogenerate -m "description"
     ↓
Inspect Revision Script in backend/migrations/versions/
     ↓
Apply Migration: alembic upgrade head
     ↓
Update Pydantic Schemas & Pytest Models
```

---

## 12. API Change Rules

1. Define or update Pydantic schemas in `backend/app/schemas/api.py`.
2. Implement route handler in `backend/app/api/routes/`.
3. If changing response field structures, update the TypeScript interface in `frontend/types/scholarship.ts` simultaneously.

---

## 13. Adding a New Feature

1. Identify affected layers (Database ➔ Services ➔ API Routes ➔ Frontend Components).
2. Implement database changes via Alembic migrations if new fields are required.
3. Add backend processing logic in `app/services/`.
4. Expose REST endpoints under `/api/v1/`.
5. Connect API endpoints to Next.js UI services (`frontend/services/`).
6. Add unit tests in `backend/tests/`.

---

## 14. Modifying Existing Features

Before altering core pipeline components (such as `OpenAIExtractor` or `ScholarshipPageFilter`):
* Trace references across `backend/app/services/scheduler/` and `backend/app/api/routes/`.
* Run existing test suites (`pytest tests/test_filter.py`, `pytest tests/test_pipeline.py`) to prevent breaking existing extraction rules.

---

## 15. Testing Requirements

### Running Tests
Execute pytest from the `backend/` directory:

```bash
# Run all unit and integration tests
pytest

# Run a specific filter test module
pytest tests/test_filter.py
```

### Coverage Expectations
* New pre-filtering or parsing routines must include corresponding test scripts under `backend/tests/`.

---

## 16. Pull Requests

* Provide a clear title detailing the feature or fix.
* List all modified endpoints, database tables, or UI components.
* Verify that all backend `pytest` unit tests pass locally prior to submitting the PR.

---

## 17. Code Review Checklist

- [ ] Code follows Python PEP 8 and TypeScript guidelines.
- [ ] No hardcoded API keys or secrets present in code or committed `.env` files.
- [ ] Pre-filter rules verified to avoid unnecessary Gemini API calls.
- [ ] Database migrations tested and applied cleanly.
- [ ] Pytest suite executed and passing.
- [ ] Frontend fallback handling confirmed working.

---

## 18. Security Rules

* **Secrets Management:** Never commit API keys (`GEMINI_API_KEY`) or production connection strings (`DATABASE_URL`). Always use environment variables.
* **Input Validation:** Use Pydantic schemas to sanitize incoming JSON payloads.

---

## 19. Documentation Rules

* Update `README.md` if installation steps or environment variable requirements change.
* Update `ARCHITECTURE.md` if adding core subsystems, database models, or new background jobs.

---

## 20. Breaking Changes

* **Backend API Breaking Changes:** If an endpoint payload must change, preserve backward compatibility by providing optional fields or versioning the endpoint path.

---

## 21. Release Process

> Not currently defined in the project.

### Recommended Release Process
1. Merge feature branch into `develop` after testing.
2. Conduct end-to-end integration test against production Supabase instance.
3. Merge `develop` into `main` to trigger automated deployments on Vercel and Koyeb.

---

## 22. Definition of Done

- [ ] Feature/bugfix fully implemented.
- [ ] Local tests executed and passing.
- [ ] `README.md` / `ARCHITECTURE.md` updated (if applicable).
- [ ] Code committed with clear messages.
- [ ] Verified live interaction between Next.js frontend and FastAPI backend.

---

## 23. Golden Rules

1. **Protect Token Quotas:** Always run raw web pages through `ScholarshipPageFilter` before calling LLM parsing routines.
2. **Never Commit Secrets:** Ensure `.env` and `.venv` remain in `.gitignore`.
3. **Keep Frontend In Sync:** Update TypeScript types whenever Pydantic response schemas change.
4. **Test Before Merging:** Always execute `pytest` before committing changes to shared branches.
