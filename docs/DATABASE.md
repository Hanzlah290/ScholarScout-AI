# Database Design

## Overview

The database stores only verified scholarship information and the metadata required to operate the system.

Downloaded webpages, intermediate AI outputs, and temporary processing data are intentionally kept outside the database. Raw pages are stored separately by the Raw Data Collector and can be reprocessed later if needed.

The database serves as the single source of truth for all verified scholarship records displayed in the dashboard.

---

# Database Philosophy

The database is designed to store only clean, validated, and verified scholarship data.

Each module in the system has a dedicated responsibility:

- The Source Connector discovers scholarship-related pages.
- The Raw Data Collector stores downloaded pages.
- The AI Extraction Module extracts structured information.
- The Validator verifies extracted data.
- The Duplicate Checker determines whether a scholarship should be inserted or updated.
- The Database stores only the final verified scholarship records.

This separation keeps the system modular, maintainable, and easy to extend.

---

# Tables

Version 1 contains four primary tables:

```
Sources
   │
   ├──────────────┐
   ▼              ▼
Scholarships   Search Logs

User Profile
(Independent)
```

---

# 1. Scholarships

Stores verified scholarship information.

| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| source_id | UUID | References the source that discovered the scholarship |
| title | Text | Scholarship title |
| university | Text | University name |
| country | Text | Country |
| degree | Text | Master's, PhD, etc. |
| field | Text | Software Engineering, Computer Science, etc. |
| funding | Text | Fully Funded, Partial, etc. |
| deadline | Date | Application deadline |
| application_link | Text | Official application link |
| source_url | Text | Original webpage URL |
| requirements | JSON | Admission requirements |
| documents_required | JSON | Required documents |
| ai_summary | Text | AI-generated summary |
| status | Text | Open / Closed |
| last_verified | Timestamp | Last successful verification |
| raw_page_path | Text | Path to the stored raw page |
| created_at | Timestamp | Record creation time |
| updated_at | Timestamp | Last update time |

---

# 2. Sources

Stores information about every configured scholarship source.

Examples:

- Tsinghua University
- Peking University
- Zhejiang University

Future versions may also include:

- CSC
- Google Search
- Facebook
- Telegram
- Scholarship Portals

| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | Text | Source name |
| base_url | Text | Website URL |
| source_type | Text | University, CSC, Google, etc. |
| enabled | Boolean | Whether the source should be scanned |
| last_checked | Timestamp | Last successful scan |
| status | Text | Healthy, Error, Offline, Disabled |

---

# 3. Search Logs

Stores information about every search execution.

This table is primarily used for debugging, monitoring, and performance analysis.

| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| source_id | UUID | Source that was scanned |
| started_at | Timestamp | Search start time |
| finished_at | Timestamp | Search completion time |
| duration_seconds | Integer | Total execution time |
| pages_scanned | Integer | Number of pages scanned |
| scholarships_found | Integer | Scholarships detected |
| new_scholarships | Integer | New scholarships added |
| status | Text | Success / Failed |
| error_message | Text | Error details if execution failed |

---

# 4. User Profile

Stores user preferences for scholarship matching.

Version 1 supports a single user.

| Field | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| target_country | Text | Preferred country |
| preferred_degree | Text | Master's, PhD, etc. |
| target_field | Text | Software Engineering, Computer Science, etc. |
| cgpa | Decimal | User CGPA |
| english_test | Text | IELTS / TOEFL / None |
| preferred_language | Text | Preferred scholarship language |
| notes | Text | Additional preferences |

---

# Relationships

The database relationships are intentionally simple in Version 1.

- One **Source** can produce many **Scholarships**.
- One **Source** can have many **Search Logs**.
- **User Profile** is independent in Version 1.

---

# Data Ownership

Each module owns its own data.

| Module | Data Owned |
|----------|------------|
| Source Connector | Website URLs |
| Keyword & URL Filter | Filtered page list |
| Raw Data Collector | Downloaded webpages |
| AI Extraction Module | Structured scholarship object |
| Validator | Verified scholarship object |
| Duplicate Checker | Insert / Update decision |
| Database | Verified scholarship records |

---

# Future Expansion

Future versions may include:

- Multiple users
- Multiple countries
- Saved scholarships
- Notifications
- Application tracking
- Scholarship categories
- AI confidence scores
- Source performance metrics
- Raw page metadata
- User activity history

---

# Design Principles

The database follows these principles:

- Store only verified scholarship information.
- Keep raw downloaded pages outside the database.
- Maintain referential integrity between sources and scholarships.
- Minimize duplicate records.
- Support future expansion without requiring major schema changes.
- Keep tables simple, normalized, and easy to maintain.