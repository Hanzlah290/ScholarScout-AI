# Troubleshooting & Diagnostic Manual — ScholarScout AI

This manual provides systematic diagnostic procedures, error resolutions, log inspection guides, and escalation strategies for developer and operational issues in **ScholarScout AI**.

---

## 1. General Debugging Methodology

When encountering an issue, follow this systematic four-step diagnostic workflow:

```text
1. Identify Failure Scope
   ├── Frontend UI (Browser Console / Network Tab)
   ├── Backend API (Uvicorn stdout logs / HTTP status codes)
   ├── Database (PostgreSQL connections / Alembic state)
   └── Background Scheduler (APScheduler logs / Gemini API limits)
     ↓
2. Verify Environment Variables & Configuration (.env files)
     ↓
3. Execute Diagnostic Commands & Unit Tests (pytest / curl)
     ↓
4. Consult Error Matrix & Resolve (See Section 17)
```

---

## 2. Application Won't Start

### Problem: Backend Server (`uvicorn app.main:app`) Fails to Launch

#### Symptom 1: `ModuleNotFoundError: No module named 'app'`
* **Cause:** Python execution path is missing the backend root context.
* **Fix:** Set `PYTHONPATH=.` before executing Uvicorn:
  ```powershell
  $env:PYTHONPATH="."
  uvicorn app.main:app --reload
  ```

#### Symptom 2: `Address already in use` (Port 8000 Conflict)
* **Cause:** Another process is utilizing port 8000.
* **Fix:** Identify and terminate the blocking process or change ports:
  ```powershell
  # Windows PowerShell:
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  
  # Or start Uvicorn on port 8001:
  uvicorn app.main:app --port 8001 --reload
  ```

---

## 3. Dependency Errors

### Python Virtual Environment Issues
* **Symptom:** `ImportError` or missing package dependencies upon launching backend server.
* **Resolution:** Re-sync Python dependencies:
  ```bash
  cd backend
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

### Node.js Frontend Dependency Mismatches
* **Symptom:** Next.js build or dev server crashes due to module resolution errors.
* **Resolution:** Clean Node cache and re-install node modules:
  ```bash
  cd frontend
  rm -rf node_modules .next package-lock.json
  npm install
  ```

---

## 4. Environment Variable Errors

### Missing Configuration Credentials
* **Symptom:** Backend crashes on startup with Pydantic `ValidationError` or runtime exceptions during database initialization.
* **Diagnosis:** Inspect `backend/.env` file. Ensure required keys are set:
  ```env
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  GEMINI_API_KEY=your_gemini_api_key
  PYTHONPATH=.
  ```
* **Frontend Symptom:** Web dashboard fails to fetch scholarships and falls back to static mock data.
* **Diagnosis:** Verify `frontend/.env.local` contains:
  ```env
  NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
  ```

---

## 5. Database Connection Errors

### Problem: Cannot Connect to PostgreSQL (`psycopg2.OperationalError`)

#### Diagnosis Steps
1. **Verify URI String:** Ensure `DATABASE_URL` starts with `postgresql://` (not `postgres://`).
2. **Network Reachability:** Verify connection to remote provider (Supabase / Neon):
   ```powershell
   # Test TCP socket connection (port 5432)
   Test-NetConnection -ComputerName db.xxx.supabase.co -Port 5432
   ```
3. **Password Special Characters:** URL-encode passwords containing special characters like `@`, `#`, or `$`.

---

## 6. Migration Errors (Alembic)

### Problem: `Target database is not up to date` or `Can't locate revision`

#### Diagnosis & Resolution
* **Run Pending Migrations:**
  ```bash
  cd backend
  alembic upgrade head
  ```
* **Conflict Resolution:** If local migration revisions conflict with remote Git branches:
  ```bash
  alembic heads
  alembic merge heads -m "merge conflicting migration heads"
  alembic upgrade head
  ```

---

## 7. REST API & Endpoint Errors

### 1. `404 Not Found` on API Endpoint
* **Cause:** Route mismatch or missing trailing prefix.
* **Fix:** Ensure base URL includes `/api/v1` (e.g., `http://localhost:8000/api/v1/scholarships`).

### 2. `422 Unprocessable Entity`
* **Cause:** Invalid query parameter types passed to FastAPI router.
* **Fix:** Check query parameter formats (`skip` and `limit` must be non-negative integers).

### 3. `CORS Error` in Browser Console
* **Cause:** Cross-Origin Resource Sharing blocking frontend origin.
* **Fix:** Ensure `CORSMiddleware` in `backend/app/main.py` explicitly allows the frontend origin domain.

---

## 8. Authentication Errors

> **Current Implementation Note:** No user authentication tokens or JWT keys are implemented for MVP endpoints. If access errors occur, verify backend network availability.

---

## 9. Frontend Errors (Next.js)

### Web Page Render Crash or Hydration Mismatch
* **Diagnosis:** Check Browser DevTools Console (`F12`).
* **Symptom:** `TypeError: Cannot read properties of undefined (reading 'map')`.
* **Cause:** API endpoint returned unexpected JSON payload structure.
* **Fix:** Verify frontend service parser in `frontend/services/scholarshipService.ts` correctly unpacks `{ scholarships: [...] }`.

---

## 10. Build Errors

### Production Next.js Build Failure (`npm run build`)
* **Symptom:** ESLint or TypeScript type-checking errors during compilation.
* **Fix:** Run explicit type checks to locate breaking interfaces:
  ```bash
  cd frontend
  npx tsc --noEmit
  ```

---

## 11. External Service & LLM Errors (Google Gemini API)

### 1. `ResourceExhausted` (HTTP 429)
* **Cause:** Gemini API quota limits reached during crawler extraction.
* **Fix:** Verify `ScholarshipPageFilter` is enabled in `backend/app/services/filters/scholarship.py` to prevent unnecessary non-scholarship page parsing.

### 2. `InvalidArgument` / Invalid API Key
* **Cause:** Invalid key string provided in `GEMINI_API_KEY`.
* **Fix:** Regenerate key at [Google AI Studio](https://aistudio.google.com) and update `backend/.env`.

---

## 12. Background Job Errors (APScheduler)

### Problem: 6-Hour Scheduler Job Fails to Run or Process Queue

#### Diagnosis Steps
1. **Check Server Uptime:** Embedded `APScheduler` runs within the FastAPI process lifecycle. If Uvicorn restarts or sleeps (e.g., Koyeb idle instance), timers pause.
2. **Inspect Database Sources:** Verify active sources exist in the database table:
   ```sql
   SELECT COUNT(*) FROM sources WHERE status = 'active';
   ```
3. **Manual Job Trigger:** Test scheduler routine outside interval timer:
   ```bash
   cd backend
   python app/scripts/run_discovery.py
   ```

---

## 13. Deployment Errors (Vercel & Koyeb)

### Koyeb Backend Deployment Crash
* **Check Logs:** Open Koyeb Dashboard ➔ **Services** ➔ **Logs Tab**.
* **Common Cause:** Missing `PYTHONPATH=.` environment variable on Koyeb service environment settings.

### Vercel Frontend API Connection Failure
* **Common Cause:** Missing `NEXT_PUBLIC_API_BASE_URL` in Vercel project environment variables.

---

## 14. Performance Problems

* **Slow Initial Scans:** Dynamic single-page application (SPA) university sites trigger Playwright fallback rendering, increasing CPU/RAM consumption.
* **Database Query Latency:** Large table sizes require indexing `created_at` and `degree_level` columns (refer to `DATABASE.md`).

---

## 15. Logging Reference

| Log Source | Location / View Command | Output Contents |
| :--- | :--- | :--- |
| **Backend Service** | stdout (Terminal where Uvicorn runs) | HTTP request logs, background scheduler logs, pre-filter scores |
| **Frontend Service** | stdout / Browser DevTools Console (`F12`) | React component rendering errors, API fetch logs |
| **Database Queries** | Enable `echo=True` in `app/database/database.py` | Raw SQL statement execution |

---

## 16. Useful Diagnostic Commands

```bash
# Test Backend Health Endpoint
curl -X GET "http://localhost:8000/api/v1/scholarships/stats"

# Run Pytest Backend Test Suite
cd backend && pytest

# Inspect Alembic Current Migration Version
cd backend && alembic current

# Test Next.js Production Build
cd frontend && npm run build
```

---

## 17. Common Error Messages & Quick Resolutions

| Error Message | Cause | Diagnosis | Solution |
| :--- | :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'app'` | Execution path missing root dir | Run `python app/main.py` directly | Set `PYTHONPATH=.` before launching server |
| `psycopg2.OperationalError: connection failed` | Bad PostgreSQL URL / network offline | Test port 5432 socket connection | Update `DATABASE_URL` in `backend/.env` |
| `Failed to fetch` in Browser Console | Backend offline or CORS issue | Check API status at `/scholarships/stats` | Verify backend running & `NEXT_PUBLIC_API_BASE_URL` |
| `ResourceExhausted` from Gemini SDK | API rate limit exceeded | Check Google AI Studio quota metrics | Ensure pre-filtering is active before LLM invocation |

---

## 18. Escalation & Problem Ownership Guide

* **Application Code Issues:** Inspect Python logic in `backend/app/services/` or TypeScript components in `frontend/components/`.
* **Database / Migration Issues:** Refer to `DATABASE.md` and inspect `backend/migrations/versions/`.
* **Deployment / Cloud Infrastructure:** Refer to `DEPLOYMENT.md` and check Koyeb / Vercel cloud service dashboards.
* **AI Model / Parsing Issues:** Inspect prompt formatting in `backend/app/services/extraction/openai_extractor.py`.
