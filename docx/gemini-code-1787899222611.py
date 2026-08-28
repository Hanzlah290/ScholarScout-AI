api_content = """# REST API Specification — ScholarScout AI

This document provides complete technical specifications for the RESTful API layer of **ScholarScout AI**, detailing operational endpoints, request/response JSON schemas, error structures, backend router files, and safe modification procedures.

---

## 1. API Overview

* **Technology Stack:** FastAPI (Python 3.11+), Pydantic v2 validation schemas, SQLAlchemy ORM persistence.
* **Protocol & Format:** Standard HTTPS / JSON requests and responses (`Content-Type: application/json`).
* **Base URL:** 
  * Development: `http://localhost:8000/api/v1`
  * Production: `https://<your-koyeb-backend-url>.koyeb.app/api/v1`
* **API Versioning:** Explicit URL prefixing (`/api/v1`).
* **Authentication:** None (Public REST endpoints for MVP).

---

## 2. Authentication

> **Current Implementation Status:** Public Access / Unauthenticated  
*Note: All currently exposed routes (`/scholarships`, `/sources`, `/scholarships/stats`) are publicly accessible without JWT tokens, API keys, or session cookies.*

---

## 3. Endpoint Summary

| Method | Endpoint | Purpose | Auth Required |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/scholarships` | Query, search, and paginate active scholarships | No |
| **GET** | `/api/v1/scholarships/stats` | Retrieve real-time pipeline and database stats | No |
| **GET** | `/api/v1/scholarships/{id}` | Fetch detailed metadata for a specific scholarship | No |
| **GET** | `/api/v1/sources` | Retrieve active Chinese university crawler sources | No |

---

## 4. Detailed Endpoint Documentation

### GET /api/v1/scholarships

#### Purpose
Fetches a paginated list of active scholarships, supporting multi-field filtering by degree level, funding type, university name, and general text search queries.

#### Authentication
None.

#### Headers
`Accept: application/json`

#### Query Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `query` | string | No | `null` | Keyword filter matching scholarship title or university name |
| `degree` | string | No | `null` | Filter by degree level (`Bachelor`, `Master`, `PhD`) |
| `funding` | string | No | `null` | Filter by funding type (`Full`, `Partial`, `Stipend`) |
| `university` | string | No | `null` | Filter by university domain or name |
| `skip` | integer | No | `0` | Pagination offset count |
| `limit` | integer | No | `20` | Max number of records to return (Max: 100) |

#### Request Body
None.

#### Response Body Schema
Returns a JSON object containing total record count and an array of `ScholarshipResponse` items:

```json
{
  "total": 42,
  "scholarships": [
    {
      "id": "c9b1a5e4-8f2a-4c12-b91d-0e24f6a91234",
      "title": "Chinese Government Scholarship (CSC) 2026",
      "university": "Tsinghua University",
      "degree_level": "Master",
      "funding_type": "Full",
      "funding_details": "Full tuition coverage, free university dormitory, comprehensive medical insurance, plus 3,000 RMB monthly stipend.",
      "deadline": "2026-04-15",
      "application_url": "[https://www.tsinghua.edu.cn/en/admissions/scholarships.htm](https://www.tsinghua.edu.cn/en/admissions/scholarships.htm)",
      "summary": "Full master degree funding program for international students covering all academic fees and living expenses.",
      "requirements": ["Bachelor degree holder", "Under 35 years old", "HSK 5 or English Proficiency Proof"],
      "created_at": "2026-08-28T10:15:00Z"
    }
  ]
}