# Database Architecture & Reference — ScholarScout AI

This document provides complete technical specifications for the relational database schema, ORM abstractions, data flow mechanisms, migrations, and modification procedures of **ScholarScout AI**.

---

## 1. Database Overview

* **Database Technology:** PostgreSQL (v14+)
* **Object-Relational Mapping (ORM):** SQLAlchemy 2.0 (Declarative Base)
* **Migration Framework:** Alembic
* **Connection Architecture:** Async/Sync Session Local connection management via `app.database.database.engine` and `SessionLocal`.
* **Environment Configuration:** Configured dynamically via `DATABASE_URL` environment variable parsed in `app.config.settings`.

```text
PostgreSQL Connection String Format:
postgresql://<user>:<password>@<host>:<port>/<dbname>
```

---

## 2. Entity-Relationship Diagram (ERD)

```mermaid
erdiagram
    scholarships {
        uuid id PK
        string title
        string university
        string degree_level
        string funding_type
        text funding_details
        string deadline
        string application_url
        text summary
        json requirements
        string source_url
        string content_hash UK
        timestamp created_at
        timestamp updated_at
    }

    sources {
        uuid id PK
        string url UK
        string name
        string status
        timestamp last_checked_at
        integer check_interval_hours
        integer failure_count
        timestamp created_at
        timestamp updated_at
    }

    search_logs {
        uuid id PK
        string query
        integer results_count
        timestamp created_at
    }

    user_profiles {
        uuid id PK
        string email UK
        string name
        timestamp created_at
    }
```

---

## 3. Tables & Schema Reference

### Table: `scholarships`
Stores verified scholarship opportunities parsed from university portals.

| Column | Type | Nullable | Default | PK | FK | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | `uuid_generate_v4()` | Yes | No | Primary key identifier |
| `title` | String(255) | No | None | No | No | Title of the scholarship program |
| `university` | String(255) | No | None | No | No | Target university name |
| `degree_level` | String(50) | No | None | No | No | Target degree (`Bachelor`, `Master`, `PhD`) |
| `funding_type` | String(50) | No | None | No | No | Funding classification (`Full`, `Partial`, `Stipend`) |
| `funding_details` | Text | Yes | None | No | No | In-depth description of financial benefits |
| `deadline` | String(100) | Yes | None | No | No | Application closing date string |
| `application_url` | String(500) | Yes | None | No | No | Direct link to official application portal |
| `summary` | Text | Yes | None | No | No | AI-generated program summary |
| `requirements` | JSON | Yes | `[]` | No | No | JSON array of eligibility rules and criteria |
| `source_url` | String(500) | No | None | No | No | Source announcement web page URL |
| `content_hash` | String(64) | No | None | No | No | SHA-256 hash for deduplication |
| `created_at` | Timestamp | No | `now()` | No | No | Record creation timestamp |
| `updated_at` | Timestamp | No | `now()` | No | No | Record last updated timestamp |

---

### Table: `sources`
Manages the queue of Chinese higher-education domains (`.edu.cn`) monitored by the crawler.

| Column | Type | Nullable | Default | PK | FK | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | `uuid_generate_v4()` | Yes | No | Primary key identifier |
| `url` | String(500) | No | None | No | No | Base portal domain or announcement URL |
| `name` | String(255) | Yes | None | No | No | Name of the educational institution |
| `status` | String(50) | No | `'active'` | No | No | Scanning state (`active`, `completed`, `error`) |
| `last_checked_at` | Timestamp | Yes | None | No | No | Timestamp of previous successful scan |
| `check_interval_hours` | Integer | No | `6` | No | No | Scanning interval frequency in hours |
| `failure_count` | Integer | No | `0` | No | No | Consecutive scan failure attempts |
| `created_at` | Timestamp | No | `now()` | No | No | Record creation timestamp |
| `updated_at` | Timestamp | No | `now()` | No | No | Record last updated timestamp |

---

### Table: `search_logs`
Logs user search queries executed on the frontend for metric tracking.

| Column | Type | Nullable | Default | PK | FK | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | `uuid_generate_v4()` | Yes | No | Primary key identifier |
| `query` | String(255) | No | None | No | No | Search query term |
| `results_count` | Integer | No | `0` | No | No | Number of scholarship matches returned |
| `created_at` | Timestamp | No | `now()` | No | No | Query execution timestamp |

---

### Table: `user_profiles`
Auxiliary user identity model for future extensions.

| Column | Type | Nullable | Default | PK | FK | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | UUID | No | `uuid_generate_v4()` | Yes | No | Primary key identifier |
| `email` | String(255) | No | None | No | No | User email address |
| `name` | String(255) | Yes | None | No | No | Display name of user |
| `created_at` | Timestamp | No | `now()` | No | No | Profile creation timestamp |

---

## 4. Relationships

* **Unlinked / Decoupled Models:** Currently, `Scholarship` and `Source` entities are logically connected via domain URLs (`source_url` matching `sources.url`), but do not enforce explicit foreign key constraints at the database engine level to optimize async batch insertions during crawler tasks.

---

## 5. Constraints

1. **Unique Constraints (`UK`):**
   * `scholarships.content_hash`: Prevents duplicate extraction persistence.
   * `sources.url`: Ensures unique domain indexing in the crawling queue.
   * `user_profiles.email`: Prevents duplicate profile generation.
2. **Primary Key Constraints (`PK`):**
   * Standard UUID v4 primary keys enforced on all tables (`id`).

---

## 6. Indexes

* `scholarships_pkey`: Primary index on `scholarships(id)`.
* `sources_pkey`: Primary index on `sources(id)`.
* `ix_scholarships_content_hash`: Unique index on `scholarships(content_hash)` for accelerated deduplication lookup.
* `ix_sources_url`: Unique index on `sources(url)` for rapid queue discovery checks.

---

## 7. Database Migrations

### Framework & Location
* **Tool:** Alembic
* **Location:** `backend/migrations/`
* **Version Scripts:** `backend/migrations/versions/`

### Migration Commands (PowerShell / Bash)

```bash
# Navigate to backend folder
cd backend

# Create a new migration revision
alembic revision --autogenerate -m "describe_changes"

# Upgrade database to latest revision
alembic upgrade head

# Rollback last applied migration
alembic downgrade -1
```

---

## 8. Data Flow

```text
Crawler / Scraper Node
  ↓ Extracts Page HTML & Generates Content Hash
Duplicate Checker (app/services/duplicate_checker/repository.py)
  ↓ Executes SELECT content_hash FROM scholarships
If Unique:
  ↓ Inserts Record via SQLAlchemy Session (app/models/scholarship.py)
PostgreSQL Database
  ↓ Row Persisted
FastAPI REST API Controller (app/api/routes/scholarships.py)
  ↓ Executes Query via SessionLocal Dependency
JSON Payload Rendered to Frontend Dashboard
```

---

## 9. Important Queries

### Active Due Sources Fetch Query
Used by the extraction pipeline background job to fetch candidate crawling targets:

```sql
SELECT * FROM sources 
WHERE status = 'active' 
  AND (last_checked_at IS NULL OR last_checked_at <= NOW() - INTERVAL '6 hours')
ORDER BY last_checked_at ASC 
LIMIT 3;
```

### Paginated Scholarship Query with Filters
Used by `GET /api/v1/scholarships`:

```sql
SELECT * FROM scholarships 
WHERE (:degree IS NULL OR degree_level = :degree)
  AND (:funding IS NULL OR funding_type = :funding)
  AND (:query IS NULL OR title ILIKE '%' || :query || '%' OR university ILIKE '%' || :query || '%')
ORDER BY created_at DESC 
LIMIT :limit OFFSET :skip;
```

---

## 10. Database Modification Guide

### Step-by-Step Field Addition
1. **Modify Model File:** Add field definition in `backend/app/models/<target_model>.py`.
2. **Generate Migration Script:** Run `alembic revision --autogenerate -m "add_field_name"`.
3. **Inspect Migration File:** Check the generated file in `backend/migrations/versions/` for accuracy.
4. **Apply Migration:** Execute `alembic upgrade head`.
5. **Update Schemas:** Add field to Pydantic models in `backend/app/schemas/api.py`.

---

## 11. Backup & Recovery

> **Implementation Status:** Managed Service Dependent  
*Note: ScholarScout AI relies on cloud database providers (such as Supabase, Neon, or Railway) to handle daily point-in-time recovery (PITR) and database snapshot backups. No local automated backup scripts exist in the repository.*

---

## 12. Database Risks & Technical Debt

1. **Missing Full-Text Search Indexes:** Text searches (`ILIKE`) on `title` and `university` fields operate via standard string matching. High table volumes will require PostgreSQL GIN indexes (`to_tsvector`).
2. **Unenforced Foreign Key Constraints:** `Scholarship` and `Source` tables are logically linked without DB-level foreign key constraints. Data integrity depends entirely on application-layer logic.
