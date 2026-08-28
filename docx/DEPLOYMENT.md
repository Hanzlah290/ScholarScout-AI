# Production Deployment Guide — ScholarScout AI

This document provides complete instructions for deploying **ScholarScout AI** to production environments, detailing infrastructure requirements, environment variables, build procedures, database setup, and platform-specific hosting steps for **Koyeb** (Backend & APScheduler), **Vercel** (Frontend Dashboard), and **Supabase / Managed PostgreSQL** (Database).

---

## 1. Deployment Architecture

```mermaid
flowchart TD
    subgraph Client Tier
        User[End User Web Browser]
    end

    subgraph Vercel CDN Global Network
        Vercel[Next.js App Router Frontend]
    end

    subgraph Koyeb Cloud Infrastructure
        Koyeb[FastAPI Container Web Service]
        Sched[Embedded APScheduler Engine]
        Koyeb --- Sched
    end

    subgraph External Cloud Services
        Supabase[(Supabase Managed PostgreSQL)]
        Gemini[Google Gemini AI API]
        UniPortals["Chinese University Websites (.edu.cn)"]
    end

    User -->|HTTPS GET| Vercel
    Vercel -->|HTTPS REST API| Koyeb
    Koyeb -->|SQLAlchemy Connection| Supabase
    Sched -->|HTTP Crawling| UniPortals
    Koyeb <-->|LLM Extraction API| Gemini
```

---

## 2. Infrastructure Requirements

| Tier | Component | Min Specifications / Provider |
| :--- | :--- | :--- |
| **Frontend** | Next.js Dashboard | Vercel (Free / Pro Tier) |
| **Backend API & Scheduler** | FastAPI App Server | Koyeb Micro Instance (512 MB RAM, 1 vCPU, Python runtime) |
| **Database** | Managed PostgreSQL | Supabase / Neon / Render (PostgreSQL v14+, 500 MB Storage) |
| **AI Processing** | Google Gemini API | Active Gemini API Key (Google AI Studio) |

---

## 3. Environment Configuration

### Backend Environment Variables (Configured in Koyeb Dashboard)

| Variable | Required | Production Value / Description | Example |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | Supabase PostgreSQL Connection URI | `postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres` |
| `GEMINI_API_KEY` | Yes | Active Google Gemini API Key | `AIzaSy...` |
| `PYTHONPATH` | Yes | Execution path configuration | `.` |

### Frontend Environment Variables (Configured in Vercel Dashboard)

| Variable | Required | Production Value / Description | Example |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Public Koyeb Backend REST API URL | `https://scholarscout-backend.koyeb.app/api/v1` |

---

## 4. Build Process

### Local Production Build Verification

#### Backend Build Check
```bash
cd backend
python -m pip install -r requirements.txt
```

#### Frontend Production Build
```bash
cd frontend
npm run build
npm run start
```

---

## 5. Step-by-Step Production Deployment

### Step 1: Deploy Database on Supabase
1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings** ➔ **Database** ➔ **Connection String** ➔ **URI**.
3. Copy the URI and substitute `[YOUR-PASSWORD]` with your database password.

### Step 2: Deploy Backend & Scheduler to Koyeb
1. Sign up on [koyeb.com](https://www.koyeb.com) and click **Create Service**.
2. Select **GitHub** as the deployment method and pick the `ScholarScout-AI` repository.
3. Set configuration parameters:
   * **Branch:** `develop` or `main`
   * **Work Directory:** `backend`
   * **Run Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   * **Exposed Port:** `8000` (HTTP)
4. Add Environment Variables:
   * `DATABASE_URL` = *(Your Supabase Connection URI)*
   * `GEMINI_API_KEY` = *(Your Gemini API key)*
   * `PYTHONPATH` = `.`
5. Click **Deploy**. Copy the public Koyeb URL (e.g., `https://scholarscout-backend.koyeb.app`).

### Step 3: Deploy Frontend to Vercel
1. Sign up on [vercel.com](https://vercel.com) and click **Add New** ➔ **Project**.
2. Import the `ScholarScout-AI` GitHub repository.
3. Configure settings:
   * **Framework Preset:** Next.js
   * **Root Directory:** Edit and set to `frontend`
4. Add Environment Variable:
   * `NEXT_PUBLIC_API_BASE_URL` = `https://scholarscout-backend.koyeb.app/api/v1`
5. Click **Deploy**.

---

## 6. Database Migrations

FastAPI automatically initializes database tables on startup via SQLAlchemy lifespan hooks (`Base.metadata.create_all`). 

For manual Alembic schema migrations:

```bash
cd backend
alembic upgrade head
```

---

## 7. Containerization (Optional Docker Deployment)

A `Dockerfile` can be used to package the backend for container registries:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Build & Run Commands
```bash
# Build Docker image
docker build -t scholarscout-backend:latest ./backend

# Run container locally
docker run -d -p 8000:8000 --env-file ./backend/.env scholarscout-backend:latest
```

---

## 8. CI/CD Workflows

> **Implementation Status:** Managed Git-Push Integration  
*Deployment automatically triggers upon pushing commits to tracked GitHub branches (`main` or `develop`) via Vercel and Koyeb webhook integrations.*

---

## 9. SSL & Domain Configuration

* **Frontend:** Vercel automatically issues Let's Encrypt TLS/SSL certificates for custom domains and standard `.vercel.app` URLs.
* **Backend:** Koyeb automatically provisions free TLS/SSL certificates for all `.koyeb.app` endpoints.

---

## 10. Background Processing & Schedulers

* **Engine:** Embedded `APScheduler` (`AsyncIOScheduler`) running inside the FastAPI application process.
* **Extraction Job:** Runs automatically every 6 hours.
* **Discovery Job:** Runs automatically every 24 hours.
* **Keep-Alive (Optional):** Set up a free service on UptimeRobot to ping `https://scholarscout-backend.koyeb.app/api/v1/scholarships/stats` every 5 minutes to prevent instance idle sleeping.

---

## 11. Health Checks

* **Health Check Endpoint:** `GET /api/v1/scholarships/stats`
* Expected HTTP Status: `200 OK`
* Response Payload:
  ```json
  {
    "open_scholarships": 128,
    "sources_count": 34,
    "last_scan": "2026-08-28T06:00:00Z",
    "pipeline_status": "Active (Next in 05h 42m)"
  }
  ```

---

## 12. Rollback Mechanics

* **Vercel Frontend:** Navigate to Vercel Dashboard ➔ **Deployments** ➔ Click `...` next to a previous build ➔ Click **Promote to Production**.
* **Koyeb Backend:** Navigate to Koyeb Dashboard ➔ **Deployments** ➔ Click **Redeploy** on a previous commit build.

---

## 13. Backup Strategy

* Managed PostgreSQL providers (Supabase / Neon) handle point-in-time recovery (PITR) and daily database snapshots automatically.

---

## 14. Troubleshooting Deployment

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **500 Internal Server Error on API** | Missing or incorrect `DATABASE_URL` | Verify PostgreSQL URI string in Koyeb Environment Variables tab |
| **Frontend displays fallback mock data** | Incorrect `NEXT_PUBLIC_API_BASE_URL` | Ensure URL points to live Koyeb URL and includes `/api/v1` suffix |
| **ModuleNotFoundError on Koyeb** | `PYTHONPATH` not set | Add `PYTHONPATH` = `.` to Koyeb Environment Variables |
| **CORS Error in Browser** | Backend blocking origin | Verify `CORSMiddleware` configuration in `backend/app/main.py` |

---

## 15. Production Deployment Checklist

- [ ] Supabase PostgreSQL database project provisioned and URI copied.
- [ ] Koyeb web service created and connected to GitHub repository (`backend` folder).
- [ ] Backend environment variables set (`DATABASE_URL`, `GEMINI_API_KEY`, `PYTHONPATH=.`).
- [ ] Koyeb deployment verified via `GET /api/v1/scholarships/stats`.
- [ ] Vercel project imported and root set to `frontend`.
- [ ] Frontend environment variable set (`NEXT_PUBLIC_API_BASE_URL`).
- [ ] End-to-end verification completed on live Vercel domain.
