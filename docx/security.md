\# Application Security Policy & Assessment — ScholarScout AI

This document details the security architecture, implemented defensive controls, threat model, potential vulnerability risks, and operational security guidelines for \*\*ScholarScout AI\*\*.

\---

\#\# 1\. Security Overview

ScholarScout AI comprises a Next.js App Router presentation layer, a FastAPI asynchronous backend server, an embedded \`APScheduler\` background crawler, and a PostgreSQL persistence database. 

\#\#\# Security Posture Summary  
\* \*\*Current Boundary:\*\* Public-facing MVP (Minimum Viable Product).  
\* \*\*Data Sensitivity:\*\* Publicly available educational scholarship announcements and university URLs. No Personally Identifiable Information (PII) or user passwords are currently processed or stored.  
\* \*\*Primary Attack Surface:\*\* Public REST API endpoints (\`/api/v1/scholarships\`), external web page crawling routines, and third-party AI LLM API interactions.

\---

\#\# 2\. Authentication

\> \*\*Status:\*\* Public Access / Unauthenticated

\* \*\*Current State:\*\* The application does not currently implement authentication mechanisms (such as JWT tokens, OAuth2, or Session cookies).  
\* \*\*Scope:\*\* All endpoints under \`/api/v1/scholarships\` and \`/api/v1/sources\` are publicly reachable.  
\* \*\*Risk Assessment:\*\* Acceptable for public read-only query endpoints; administrative queue endpoints require access controls prior to production exposure.

\---

\#\# 3\. Authorization

\> \*\*Status:\*\* Unenforced Role-Based Access Control (RBAC)

\* \*\*Current State:\*\* There are no user roles (\`admin\`, \`user\`, \`analyst\`) or access-control lists implemented in the backend logic.  
\* \*\*Scope:\*\* Any client reaching the backend API can query database stats or list monitored domain sources.

\---

\#\# 4\. Secret Management

\#\#\# Implemented Controls  
\* \*\*Environment Variable Isolation:\*\* API credentials (\`GEMINI\_API\_KEY\`) and database URIs (\`DATABASE\_URL\`) are loaded strictly from external environment files (\`backend/.env\`) via Pydantic \`BaseSettings\` (\`app.config.settings\`).  
\* \*\*Git Exclusion Rules:\*\* Root \`.gitignore\` and \`backend/.gitignore\` explicitly exclude \`.env\`, \`.env.local\`, \`.venv\`, and \`\_\_pycache\_\_\` directories to prevent accidental credential commits to GitHub repositories.

\#\#\# Operational Rules  
\* \*\*No Hardcoded Credentials:\*\* Plaintext secrets, private keys, or passwords must never be committed to source control.

\---

\#\# 5\. Input Validation & Data Sanitization

\#\#\# Backend (Python / FastAPI)  
\* \*\*Schema Validation:\*\* Request query parameters (\`skip\`, \`limit\`, \`degree\`, \`funding\`) are coerced and validated using Pydantic schemas (\`app.schemas.api.py\`). Invalid data types trigger an automatic \`422 Unprocessable Entity\` response.  
\* \*\*SQL Injection Prevention:\*\* Database queries utilize SQLAlchemy 2.0 ORM parameterization, eliminating raw SQL string concatenations and preventing SQL Injection (SQLi) attacks.

\#\#\# Pre-Filter Engine  
\* \*\*Content Sanitization:\*\* Raw HTML fetched from crawled portals is sanitized using BeautifulSoup4 text extraction and regular expression matching (\`ScholarshipPageFilter\`) before processing.

\---

\#\# 6\. API Security

\#\#\# Implemented Controls  
\* \*\*CORS (Cross-Origin Resource Sharing):\*\* Standard \`CORSMiddleware\` configured on the FastAPI instance in \`app/main.py\`.

\#\#\# Missing Controls  
\* \*\*Rate Limiting:\*\* No rate-limiting middleware (e.g., \`slowapi\`) is currently enforced to limit API request bursts per client IP address.

\---

\#\# 7\. Database Security

\* \*\*ORM Parameterization:\*\* Queries execute strictly via SQLAlchemy session abstractions (\`get\_db\` dependency).  
\* \*\*Connection Strings:\*\* Production database strings utilize TLS/SSL encrypted connection URIs provided by cloud hosters (Supabase/Neon).

\---

\#\# 8\. Frontend Security (Next.js)

\* \*\*XSS Prevention:\*\* React's default JSX output encoding automatically escapes string variables rendered in the DOM, mitigating Cross-Site Scripting (XSS).  
\* \*\*Environment Variable Isolation:\*\* Only variables explicitly prefixed with \`NEXT\_PUBLIC\_\` (such as \`NEXT\_PUBLIC\_API\_BASE\_URL\`) are exposed to the client-side JavaScript bundle.

\---

\#\# 9\. External Service Security

\#\#\# Google Gemini AI API  
\* \*\*Communication:\*\* Encrypted HTTPS requests over TLS 1.3 to Google AI Studio infrastructure.  
\* \*\*API Key Protection:\*\* The Gemini API key is maintained exclusively on the backend server and is never passed to or exposed in the frontend client code.

\#\#\# University Web Crawler  
\* \*\*Egress Traffic:\*\* HTTPX and Playwright issue outbound requests to external \`.edu.cn\` university portals.  
\* \*\*Timeout Enforcement:\*\* Network requests incorporate default execution timeouts to prevent resource starvation.

\---

\#\# 10\. Logging Security Guidelines

\#\#\# What SHOULD Be Logged  
\* Pipeline execution timestamps (scan started, scan completed).  
\* Crawler HTTP error status codes (e.g., \`404 Not Found\`, \`503 Service Unavailable\`).  
\* Unhandled exception backtraces (sanitized).

\#\#\# What MUST NOT Be Logged  
\* Full database connection strings containing embedded passwords (\`DATABASE\_URL\`).  
\* Raw API key strings (\`GEMINI\_API\_KEY\`).  
\* Auth headers or authorization tokens (when added in future releases).

\---

\#\# 11\. Dependency Security

\* \*\*Python Dependencies:\*\* Maintained in \`backend/requirements.txt\` (\`fastapi\`, \`uvicorn\`, \`sqlalchemy\`, \`pydantic\`, \`google-generativeai\`).  
\* \*\*Node Dependencies:\*\* Maintained in \`frontend/package.json\` (\`next\`, \`react\`, \`tailwindcss\`).  
\* \*\*Recommendation:\*\* Developers should periodically run dependency vulnerability scanners (\`pip audit\` for Python, \`npm audit\` for Node.js).

\---

\#\# 12\. Codebase Security Risk Analysis

| Risk | Severity | Location | Explanation | Recommendation |  
| :--- | :--- | :--- | :--- | :--- |  
| \*\*Unauthenticated Source Queue Access\*\* | Medium | \`backend/app/api/routes/sources.py\` | Route exposing active crawling target URLs is publicly accessible without authentication. | Implement API key or JWT bearer token protection for admin management endpoints. |  
| \*\*Missing API Rate Limiting\*\* | Medium | \`backend/app/api/routes/scholarships.py\` | Endpoints lack request rate limiting, exposing the API to potential Denial of Service (DoS) or scraping abuse. | Add \`slowapi\` rate-limiting middleware (e.g., max 100 requests per minute per IP). |  
| \*\*Unrestricted CORS Configuration\*\* | Low | \`backend/app/main.py\` | \`allow\_origins=\["\*"\]\` allows any web domain to issue cross-origin requests to the API during local development. | Restrict \`allow\_origins\` to the specific production domain of the Next.js frontend in deployment environments. |

\---

\#\# 13\. Implemented Security Controls

\- \[x\] Environment variable isolation for sensitive credentials (\`.env\`).  
\- \[x\] Sensitive files and directories excluded in \`.gitignore\`.  
\- \[x\] Parameterized SQL queries via SQLAlchemy ORM.  
\- \[x\] Strict input schema validation via Pydantic models.  
\- \[x\] Automatic JSX DOM escaping against XSS in React components.  
\- \[x\] Server-side isolation of third-party AI API keys.

\---

\#\# 14\. Missing Security Controls (Technical Debt)

\- \[ \] Authentication / Authorization mechanism (JWT / OAuth2).  
\- \[ \] API Rate Limiting (\`slowapi\` integration).  
\- \[ \] Production-restricted CORS origin policy.  
\- \[ \] Automated vulnerability scanning (GitHub Actions / Dependabot).

\---

\#\# 15\. Security Verification Checklist

Before deploying changes to production:

\- \[ \] Verify no \`.env\` or credential files are staged in Git (\`git status\`).  
\- \[ \] Ensure all backend queries use SQLAlchemy ORM abstractions.  
\- \[ \] Confirm \`GEMINI\_API\_KEY\` is referenced solely inside backend modules.  
\- \[ \] Run \`npm audit\` and \`pip audit\` to check for dependency vulnerabilities.

\---

\#\# 16\. Incident Response & Vulnerability Reporting

\#\#\# Reporting Security Issues  
If you discover a potential security vulnerability within \*\*ScholarScout AI\*\*:  
1\. \*\*Do NOT\*\* open a public GitHub issue.  
2\. Report the vulnerability privately to the project maintainers.  
3\. Include detailed steps to reproduce the issue, potential impact, and suggested remediations.  
