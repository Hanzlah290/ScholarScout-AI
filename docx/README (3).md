# ScholarScout AI

> Automated Chinese university scholarship discovery & LLM-powered extraction engine with a dynamic management dashboard.

**Status:** Active Development / Feature Complete for MVP  
**Version:** 1.0.0-dev

---

## 2. Project Overview

**ScholarScout AI** is an end-to-end automated pipeline and web application designed to eliminate manual tracking of international scholarship opportunities from Chinese university websites (`.edu.cn`). 

### Problem It Solves
University scholarship portals across China frequently update announcements across fragmented subdomains with varying HTML structures, unstructured tables, and downloadable PDF attachments. Manual extraction is time-consuming, repetitive, and prone to missing tight application windows.

### What It Does
1. **Automated Source Discovery (24-Hour Job):** Discovers and seeds active Chinese higher-education domains into the processing queue.
2. **Scholarship Extraction Layer (6-Hour Job):** Continuously crawls queued university portals, fetches raw HTML/PDF documents, performs pre-filtering to remove noise, and leverages **Google Gemini API** to extract structured JSON metadata (funding limits, eligibility rules, degree levels, and deadlines).
3. **Data Verification & Storage:** Validates eligibility criteria, checks for duplicate announcements, and persists verified opportunities into a PostgreSQL database.
4. **Web Dashboard:** Exposes a responsive Next.js web application for users to filter, search, view detailed breakdown rules, and navigate directly to official university application links.

### Target Users
* International students seeking degree or research scholarship opportunities in China.
* Educational consultants and academic advisors tracking university admissions announcements.

---

## 3. Key Features

### Backend & Automation Pipeline
* **Background Scheduler:** Powered by `APScheduler` (`AsyncIOScheduler`) running persistent discovery and extraction jobs.
* **Smart Filtering:** Pre-filters candidate raw web pages (`ScholarshipPageFilter`) before passing content to LLMs to minimize API token costs.
* **LLM Extraction Engine:** Uses `google-generativeai` (Gemini API) for structured field extraction from complex web markup and multi-page documents.
* **PDF Evidence Parsing:** Downloads, verifies, and extracts text/evidence from attached PDF announcement documents.
* **Deduplication Engine:** Implements content hashing and repository-level duplicate checking to prevent redundant database writes.
* **State & Backoff Management:** Tracks source states (`active`, `completed`, `error`) and applies automatic retry/backoff policies.

### Frontend Dashboard
* **Dynamic Analytics Header:** Real-time statistics displaying total open scholarships, active sources scanned, and next scheduler run countdown.
* **Scholarship Discovery Grid:** Dynamic filtering by degree level, funding type, university name, and search queries.
* **Detailed Breakdown Page:** Dedicated dynamic route (`/scholarships/[id]`) presenting eligibility criteria, funding details, and full AI-generated summaries.
* **Direct Application Portals:** Quick-action buttons linking directly to verified official university application pages.

---

## 4. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | Next.js (App Router, TypeScript) | Responsive web interface & dynamic dashboard |
| **Styling & Components** | Tailwind CSS, Shadcn UI / Lucide React | Modern UI design system & responsive layout |
| **Backend Framework** | FastAPI (Python 3.11+) | High-performance async REST API framework |
| **Task Scheduling** | APScheduler (`AsyncIOScheduler`) | Background execution of 6-hour extraction & 24-hour discovery jobs |
| **AI / LLM Engine** | Google Gemini API (`google-generativeai`) | Unstructured page parsing and structured scholarship metadata extraction |
| **Database & ORM** | PostgreSQL, SQLAlchemy, Alembic | Persistent relational database storage & database migration management |
| **HTTP Client & Parsing** | HTTPX, BeautifulSoup4, Playwright | Web crawling, HTML retrieval, dynamic page rendering, and PDF processing |
| **Testing Framework** | Pytest | Backend unit tests, integration tests, and crawler validation |

---

## 5. High-Level Architecture

```mermaid
flowchart TD
    subgraph Discovery & Scheduler
        SJ[APScheduler Engine] -->|Every 24 Hours| DJ[Source Discovery Job]
        SJ -->|Every 6 Hours| EJ[Extraction Job]
    end

    subgraph Crawler & AI Pipeline
        DJ -->|Discover .edu.cn domains| DB[(PostgreSQL Database)]
        EJ -->|Fetch Due Sources| Fetcher[HTTPX / Playwright Crawler]
        Fetcher --> Filter[Scholarship Page Filter]
        Filter -->|Candidate Pages| LLM[Gemini API Extractor]
        LLM --> Dedupe[Duplicate Checker & Validator]
        Dedupe -->|Persist Valid Record| DB
    end

    subgraph Presentation Layer
        DB -->|SQLAlchemy ORM| API[FastAPI REST API]
        API -->|JSON Endpoints| Web[Next.js Frontend]
        Web -->|User Interaction| User((End User))
    end
```

---

## 6. Project Structure

```text
ScholarScout-AI/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI route handlers (scholarships, sources, stats)
│   │   ├── config/              # Application configuration & Pydantic settings
│   │   ├── database/            # Database session setup and SQLAlchemy engine
│   │   ├── dependencies/        # FastAPI dependency injection helpers
│   │   ├── models/              # SQLAlchemy database ORM models (Scholarship, Source, etc.)
│   │   ├── schemas/             # Pydantic schemas for request/response validation
│   │   ├── scripts/             # Standalone runner scripts (e.g., run_discovery.py)
│   │   ├── services/
│   │   │   ├── automation/      # Discovery manager, source validator, and queue automation
│   │   │   ├── collector/       # HTML content collectors & filesystem helpers
│   │   │   ├── connectors/      # University metrics and network connectors
│   │   │   ├── duplicate_checker/# Deduplication rules and repository checks
│   │   │   ├── extraction/      # Gemini AI prompt extraction & PDF evidence processing
│   │   │   ├── filters/         # Page pre-filtering logic before LLM extraction
│   │   │   ├── pdf/             # PDF downloaders, link discovery, and text extraction
│   │   │   ├── scheduler/       # APScheduler service and discovery background jobs
│   │   │   └── validator/       # Scholarship data validation pipeline
│   │   └── main.py              # FastAPI application entrypoint & lifespan initialization
│   ├── migrations/              # Alembic database migration files
│   ├── tests/                   # Pytest test suite (filters, extraction, scheduler, endpoints)
│   ├── pytest.ini               # Pytest configuration
│   └── requirements.txt         # Backend Python dependencies
├── frontend/
│   ├── app/                     # Next.js App Router pages (Root page, dynamic /scholarships/[id])
│   ├── components/              # React UI components (Navbar, StatsSection, Cards, Layout)
│   ├── lib/                     # Frontend utilities and helper functions
│   ├── mock/                    # Mock datasets for fallback client testing
│   ├── services/                # API client integration (scholarshipService.ts)
│   ├── types/                   # TypeScript interfaces for API models
│   ├── next.config.ts           # Next.js configuration
│   └── package.json             # Frontend Node.js dependencies
└── docs/
    └── ROADMAP.md               # Project roadmap and technical milestone tracking
```

---

## 7. Prerequisites

Ensure the following runtimes and tools are installed on your environment:

* **Python:** `v3.11+`
* **Node.js:** `v18.0.0+` (with `npm` or `pnpm`)
* **PostgreSQL:** `v14.0+` (or a managed provider like Supabase/Neon)
* **Google Gemini API Key:** Active key from Google AI Studio.

---

## 8. Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Hanzlah290/ScholarScout-AI.git
cd ScholarScout-AI
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate a Python virtual environment
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node modules
npm install
```

---

## 9. Environment Variables

Create `.env` files in both the `backend/` and `frontend/` directories as detailed below.

### Backend (`backend/.env`)

| Variable | Required | Purpose | Example |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://postgres:pass@localhost:5432/scholarscout` |
| `GEMINI_API_KEY` | Yes | API Key for Gemini LLM extraction | `AIzaSy...` |
| `PYTHONPATH` | Yes | Set Python execution path | `.` |

### Frontend (`frontend/.env.local`)

| Variable | Required | Purpose | Example |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Base URL for the FastAPI backend API | `http://localhost:8000/api/v1` |

---

## 10. Running the Project

### Running the Backend Server & Background Scheduler
From the `backend/` directory with virtual environment activated:

```bash
# Option 1: Direct Uvicorn start
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using the python runner script
python run_server.py
```
*(FastAPI lifespan event automatically runs database migrations and starts the background `APScheduler`)*

### Running the Frontend Application
From the `frontend/` directory:

```bash
npm run dev
```

Open your browser at `http://localhost:3000` to access the application dashboard.

---

## 11. Testing

The backend includes a suite of test scripts covering pre-filters, PDF processors, Gemini extraction logic, and discovery jobs.

Run tests from the `backend/` folder:

```bash
# Set PYTHONPATH and execute pytest
pytest

# Run a specific unit test module
pytest tests/test_filter.py
```

---

## 12. Development

### Key Development Locations
* **API Route Endpoints:** `backend/app/api/routes/`
* **Database Models:** `backend/app/models/`
* **Extraction & AI Logic:** `backend/app/services/extraction/`
* **Pre-Filtering Rules:** `backend/app/services/filters/scholarship.py`
* **Frontend Pages & Components:** `frontend/app/` and `frontend/components/`

For detailed technical specifications, architecture diagrams, and contribution rules, refer to the documentation section below.

---

## 13. Documentation

| Document | Purpose |
| :--- | :--- |
| **`README.md`** | Project overview, setup, running instructions, and architecture |
| **`docs/ROADMAP.md`** | Project roadmap, implementation status, and feature milestones |

---

## 14. Common Commands

| Command | Purpose |
| :--- | :--- |
| `uvicorn app.main:app --reload` | Run local FastAPI backend with hot reloading |
| `python app/scripts/run_discovery.py` | Manually trigger the source discovery pipeline |
| `pytest` | Execute backend test suite |
| `npm run dev` | Run local Next.js development server |
| `npm run build` | Build production bundle for Next.js frontend |

---

## 15. Project Status

* **Maturity:** MVP / Active Development
* **Implemented Features:**
  * Complete source discovery & validation module (`.edu.cn` domain scanning).
  * Scholarship pre-filtering engine to reduce LLM payload.
  * Gemini API integration for structured extraction from web pages and PDF evidence.
  * Continuous scheduler with APScheduler.
  * Full FastAPI REST API layer (`/scholarships`, `/sources`, `/stats`).
  * Interactive Next.js frontend dashboard with dynamic detail view pages.
* **Known Limitations:**
  * Dynamic JavaScript-heavy single-page applications (SPAs) require Playwright fallback rendering which increases execution latency.

---

## 16. Important Notes

* **Port Availability:** Ensure port `8000` (Backend) and port `3000` (Frontend) are available before launching local servers.
* **API Rate Limits:** Gemini API rate limits apply during initial source seeding. The pre-filter module (`ScholarshipPageFilter`) handles early rejection of non-scholarship pages to conserve quota.

---

## 17. License

No license information found in the project.
