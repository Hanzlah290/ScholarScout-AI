# Developer Guide — ScholarScout AI

This document serves as the comprehensive, practical manual for engineers actively developing, debugging, and extending **ScholarScout AI**. 

---

## 1. Development Environment

### Supported Operating Systems
* **Windows:** Windows 10/11 (PowerShell or WSL 2 recommended)
* **Linux:** Ubuntu 22.04 LTS or equivalent
* **macOS:** macOS Monterey or newer

### Required Runtimes & Tooling
* **Python:** `v3.11+`
* **Node.js:** `v18.0.0+` (LTS)
* **Package Managers:** `pip` (Python), `npm` or `pnpm` (Node.js)
* **Database Engine:** PostgreSQL `v14+` (Local instance or remote Supabase/Neon instance)
* **Recommended Editor:** VS Code (with Python, Pylance, Tailwind CSS, and ESLint extensions)

---

## 2. Setup & Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/Hanzlah290/ScholarScout-AI.git
cd ScholarScout-AI
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
# Open a new terminal from project root
cd frontend

# Install dependencies
npm install
```

---

## 3. Environment Configuration

### Backend Environment File (`backend/.env`)
Create a `.env` file inside the `backend/` directory:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/scholarscout
GEMINI_API_KEY=your_google_gemini_api_key
PYTHONPATH=.
```

### Frontend Environment File (`frontend/.env.local`)
Create a `.env.local` file inside the `frontend/` directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 4. Running Local Services

### Start Backend API & Embedded APScheduler
From the `backend/` folder (with `.venv` activated):

```bash
# Start FastAPI with live reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Note: The FastAPI lifespan event automatically initializes database models (`Base.metadata.create_all`) and starts the `APScheduler` background service.*

### Start Frontend Next.js Server
From the `frontend/` folder:

```bash
npm run dev
```
Navigate to `http://localhost:3000` in your web browser.

---

## 5. Development Command Quick Reference

| Action | Path | Command |
| :--- | :--- | :--- |
| **Run Backend API** | `backend/` | `uvicorn app.main:app --reload` |
| **Run Python Tests** | `backend/` | `pytest` |
| **Trigger Discovery Manual Run**| `backend/` | `python app/scripts/run_discovery.py` |
| **Run Database Migration** | `backend/` | `alembic upgrade head` |
| **Run Frontend UI** | `frontend/` | `npm run dev` |
| **Build Frontend Bundle** | `frontend/` | `npm run build` |

---

## 6. Codebase Architecture Map

```text
ScholarScout-AI/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # REST API endpoints (scholarships, sources, stats)
│   │   ├── database/           # Engine setup & DB session dependency
│   │   ├── models/             # SQLAlchemy ORM schemas
│   │   ├── schemas/            # Pydantic validation definitions
│   │   ├── services/
│   │   │   ├── extraction/     # Gemini LLM prompts & PDF parsing
│   │   │   ├── filters/        # Page pre-filtering heuristic logic
│   │   │   ├── scheduler/      # APScheduler job definitions
│   │   │   └── validator/      # Eligibility validation rules
│   │   └── main.py             # App instantiation & lifespan manager
│   ├── migrations/             # Alembic migration scripts
│   └── tests/                  # Pytest modules
└── frontend/
    ├── app/                    # Next.js App Router (Root layout, page.tsx, dynamic routes)
    ├── components/             # React visual components (Navbar, Cards, Stats)
    ├── services/               # API service layer (scholarshipService.ts)
    └── types/                  # TypeScript interface definitions
```

---

## 7. Development Workflow

```text
1. Identify Issue or Feature Request
     ↓
2. Check Out Target Branch (develop or feature/*)
     ↓
3. Modify Backend Logic / Schemas / Frontend UI
     ↓
4. Run Unit Tests (pytest) & Manual Endpoint Verification
     ↓
5. Confirm Frontend State Update & Integration
     ↓
6. Commit & Push Changes
```

---

## 8. Feature Development Process

When adding a complete end-to-end feature:
1. **Database Layer:** Add or update fields in `app/models/` and run `alembic revision --autogenerate`.
2. **Schema Layer:** Update request/response models in `app/schemas/api.py`.
3. **Business/Services Layer:** Add domain logic in `app/services/`.
4. **API Layer:** Expose router endpoint in `app/api/routes/`.
5. **Frontend Layer:** Update TypeScript definitions (`frontend/types/`) and API client (`frontend/services/scholarshipService.ts`), then build components (`frontend/components/`).

---

## 9. Debugging Guide

### Inspecting Backend Logs
Uvicorn streams logs directly to stdout in your active terminal. Background jobs (`APScheduler`), crawler pre-filters, and Gemini API parsing print structured logging directly to the console.

### Inspecting Database Queries
Set SQL echo logging in `backend/app/database/database.py` during local debugging:
```python
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
```

### Inspecting Frontend API Calls
Open Chrome DevTools ➔ **Network Tab** ➔ Filter by `Fetch/XHR` to inspect requests to `http://localhost:8000/api/v1/scholarships`.

---

## 10. Testing

Refer to `TESTING.md` for full test documentation. Quick execution:

```bash
cd backend
pytest tests/test_filter.py
```

---

## 11. Database Development

Refer to `DATABASE.md` for full schema reference and migration workflows.

---

## 12. API Development

Refer to `API.md` for endpoint routes, request/response schemas, and HTTP status codes.

---

## 13. Frontend Component & Page Rules

* **Pages Structure:**
  * Root Dashboard: `frontend/app/page.tsx`
  * Dynamic Detail View: `frontend/app/scholarships/[id]/page.tsx`
* **Components Layout:**
  * `DashboardClient.tsx`: Interactive state holder for degree, funding, and search filters.
  * `StatsSection.tsx`: Metrics header displaying scholarship counts and scheduler status.
  * `Navbar.tsx`: Header navigation bar.
* **API Calls:** Component pages must call `scholarshipService.ts` rather than triggering standalone `fetch` requests.

---

## 14. Developing Background Jobs

Background jobs reside under `backend/app/services/scheduler/`:
* `discovery_job.py`: Defines `run_scheduled_discovery` (6-hour extraction) and `run_scheduled_source_discovery` (24-hour domain scan).
* **Testing Jobs Manually:** Run standalone scripts without waiting for APScheduler triggers:
  ```bash
  python -c "import asyncio; from app.services.scheduler.discovery_job import run_scheduled_source_discovery; asyncio.run(run_scheduled_source_discovery())"
  ```

---

## 15. AI & External Integration Testing

When testing Gemini LLM extraction locally:
* Ensure `GEMINI_API_KEY` is loaded in `backend/.env`.
* Standard pre-filters (`ScholarshipPageFilter`) run prior to API calls. To bypass pre-filters during local prompt testing, call `OpenAIExtractor` directly from a standalone test file in `tests/`.

---

## 16. Build Process

### Production Build Verification

```bash
# Test Next.js Production Build locally
cd frontend
npm run build
npm run start
```

---

## 17. Common Development Mistakes

1. **Bypassing the Pre-Filter:** Calling `OpenAIExtractor` on every fetched web page without passing through `ScholarshipPageFilter` will rapidly exhaust Gemini API quotas.
2. **Missing `PYTHONPATH=.`:** Running backend scripts directly without setting `PYTHONPATH=.` will cause `ModuleNotFoundError: No module named 'app'`.
3. **Hardcoding API Endpoints:** Hardcoding backend URLs inside Next.js components instead of referencing `NEXT_PUBLIC_API_BASE_URL`.

---

## 18. Quick Developer Checklist

- [ ] `.venv` active and `PYTHONPATH=.` configured.
- [ ] Database running with latest migrations applied (`alembic upgrade head`).
- [ ] Both Uvicorn (`:8000`) and Next.js (`:3000`) dev servers running.
- [ ] Pytest suite executed and passing cleanly before committing.
