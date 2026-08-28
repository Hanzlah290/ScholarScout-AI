# Developer Troubleshooting & Diagnostic Manual — ScholarScout AI

This manual provides systematic diagnostic procedures, error resolutions, and debugging commands to help developers independently troubleshoot and resolve issues across the **ScholarScout AI** stack.

---

## 1. General Debugging Methodology

When encountering an unexpected failure, follow this structured diagnostic sequence:

```text
1. Identify Failure Scope (Frontend UI, FastAPI API, Database, or Crawler Pipeline)
     ↓
2. Inspect Application Logs (Uvicorn console output or browser DevTools)
     ↓
3. Verify Environment Configuration (backend/.env & frontend/.env.local)
     ↓
4. Verify Network & Port Availability (Port 8000 for Backend, Port 3000 for Frontend)
     ↓
5. Check Database Connectivity & Migrations (SQLAlchemy connection string)
     ↓
6. Isolate Engine Dependencies (Gemini API quota, HTTPX timeouts)
```

---

## 2. Application Won't Start

### Problem: FastAPI Backend Fails on Launch (`uvicorn app.main:app`)

* **Symptom:** Terminal throws `ModuleNotFoundError: No module named 'app'` or `ImportError`.
* **Cause:** Python execution path (`PYTHONPATH`) is missing or virtual environment (`.venv`) is inactive.
* **Resolution:**
  ```powershell
  # Activate virtual environment
  .\.venv\Scripts\Activate.ps1

  # Ensure PYTHONPATH is set to project root
  $env:PYTHONPATH="."
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

### Problem: Next.js Frontend Fails on Launch (`npm run dev`)

* **Symptom:** `Error: Cannot find module` or port `3000` collision.
* **Cause:** `node_modules` not installed or port `3000` is occupied by another process.
* **Resolution:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

---

## 3. Dependency Errors

### Problem: Missing Python Packages or Version Mismatches
* **Symptom:** `ModuleNotFoundError: No module named 'google.generativeai'` or `sqlalchemy`.
* **Resolution:** Re-install frozen dependency versions from `requirements.txt`:
  ```bash
  cd backend
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

---

## 4. Environment Variable Errors

### Problem: Pydantic Validation Errors on Application Launch

* **Symptom:** `pydantic_settings.exceptions.SettingsError: ValidationError for Settings`
* **Cause:** Required environment variables (`DATABASE_URL`, `GEMINI_API_KEY`) are missing from `backend/.env`.
* **Resolution:** Ensure `backend/.env` exists and contains valid values:
  ```env
  DATABASE_URL=postgresql://postgres:password@localhost:5432/scholarscout
  GEMINI_API_KEY=AIzaSy...
  PYTHONPATH=.
  ```

---

## 5. Database Connection Errors

### Problem: SQLAlchemy Cannot Connect to PostgreSQL

* **Symptom:** `psycopg2.OperationalError: could not connect to server: Connection refused` or `FATAL: password authentication failed`.
* **Diagnosis Steps:**
  1. Test database port accessibility (default PostgreSQL port: `5432`).
  2. Verify credentials in `DATABASE_URL`.
  3. If using Supabase/Neon, ensure your IP address is allowed and TLS connection parameter (`?sslmode=require`) is appended if necessary.
* **Resolution:** Update `DATABASE_URL` in `backend/.env` and re-test connection.

---

## 6. Migration Errors

### Problem: Alembic Migration Out of Sync

* **Symptom:** `alembic.util.exc.CommandError: Target database is not up to date.` or duplicate column errors.
* **Resolution:**
  ```bash
  cd backend
  # Check current revision status
  alembic current

  # Upgrade database schema to latest version
  alembic upgrade head
  ```

---

## 7. API Errors

### Problem: HTTP 500 Internal Server Error on `/api/v1/scholarships`
* **Cause:** Database query failure or invalid JSON serialization.
* **Diagnosis:** Inspect Uvicorn terminal backtrace. If the failure mentions `funding_details` or string capacity limits, verify that Alembic migration `7334f1379176_increase_scholarship_funding_field` has been applied.

---

## 8. Authentication Errors

> **Note:** The current MVP endpoints (`/scholarships`, `/sources`, `/stats`) are publicly accessible without authentication. If connection dropouts occur between the frontend and backend, inspect CORS configuration in `backend/app/main.py`.

---

## 9. Frontend Errors

### Problem: UI Renders Static Mock Data Instead of Live Database Data
* **Cause:** Next.js frontend is failing to reach the FastAPI backend or `NEXT_PUBLIC_API_BASE_URL` is configured incorrectly.
* **Diagnosis:** Open Browser DevTools ➔ **Console Tab** ➔ Look for `API Fetch Error: Failed to fetch`.
* **Resolution:** Ensure `frontend/.env.local` points to `http://localhost:8000/api/v1` and that Uvicorn is actively running.

---

## 10. Build Errors

### Problem: Next.js Production Build Fails (`npm run build`)
* **Symptom:** TypeScript compilation error or missing type interface.
* **Resolution:** Verify `frontend/types/scholarship.ts` matches the Pydantic schema returned by `backend/app/schemas/api.py`.

---

## 11. External API Errors

### Problem: Gemini API Extraction Returns Empty Data or Rate Limit Error
* **Symptom:** `google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded` or `GoogleAPICallError`.
* **Cause:** Gemini API quota exhausted due to excessive un-filtered page requests.
* **Resolution:** Ensure raw web pages pass through `ScholarshipPageFilter` prior to invoking `OpenAIExtractor`. Verify your API key at Google AI Studio.

---

## 12. Background Job & Scheduler Errors

### Problem: 6-Hour Scholarship Extraction Job Does Not Run
* **Cause:** `APScheduler` engine failed during FastAPI lifespan startup.
* **Diagnosis:** Search Uvicorn logs for `[Scheduler] Initializing APScheduler...`.
* **Manual Trigger Verification:** Run discovery manually via CLI:
  ```bash
  cd backend
  python app/scripts/run_discovery.py
  ```

---

## 13. Deployment Errors

### Problem: Koyeb Backend Service Status "CrashLoopBackOff"
* **Cause:** Missing `PYTHONPATH=.` environment variable or missing runtime dependencies.
* **Resolution:** In Koyeb Environment Variables tab, set `PYTHONPATH` = `.` and verify Uvicorn launch command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

---

## 14. Performance Problems

### Problem: Crawling Pipeline Latency High
* **Cause:** Processing dynamic JavaScript single-page applications (SPAs) falling back to Playwright headless browser rendering.
* **Resolution:** Pre-filter static pages first (`ScholarshipPageFilter`) and allocate sufficient RAM resources on cloud instances.

---

## 15. Log Inspection Summary

| Service | Log Location | Purpose |
| :--- | :--- | :--- |
| **FastAPI Backend** | Terminal Stdout / Uvicorn Console | Inspect API requests, SQLAlchemy queries, and scheduler jobs |
| **Next.js Frontend** | Terminal Stdout / Chrome DevTools Console | Inspect React hydration, SSR, and API client errors |
| **Koyeb Host** | Koyeb Dashboard ➔ Runtime Logs | Inspect production container health and system crashes |
| **Vercel Host** | Vercel Dashboard ➔ Functions Logs | Inspect production frontend build and edge function failures |

---

## 16. Diagnostic Command Quick Reference

```bash
# Backend: Check Pytest test suite health
cd backend && pytest

# Backend: Test manual discovery pipeline execution
python app/scripts/run_discovery.py

# Backend: Apply database migrations
alembic upgrade head

# Frontend: Check production build errors
cd frontend && npm run build
```

---

## 17. Common Error Table

| Error Message | Root Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'app'` | `PYTHONPATH` variable not exported | Run `$env:PYTHONPATH="."` or set `PYTHONPATH=.` in `.env` |
| `psycopg2.OperationalError: Connection refused` | PostgreSQL database down or URI invalid | Verify `DATABASE_URL` in `.env` and database status |
| `429 Quota Exceeded (Gemini API)` | API rate limit hit | Check `ScholarshipPageFilter` scoring to avoid extra API calls |
| `CORS request blocked` | Missing allowed origin in FastAPI | Check `CORSMiddleware` in `backend/app/main.py` |

---

## 18. Escalation Guide

If you cannot resolve an issue using this guide:

1. **Codebase Issues:** Trace the execution path using `ARCHITECTURE.md` and `DEVELOPMENT.md`.
2. **Database Issues:** Inspect model declarations in `backend/app/models/` and check schema state in `DATABASE.md`.
3. **Deployment Issues:** Review platform-specific hosting steps in `DEPLOYMENT.md`.
