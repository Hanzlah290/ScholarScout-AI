# API Documentation

## Overview

The Backend API provides verified scholarship data to the frontend dashboard.

The frontend must **never communicate directly with the database**. All data is accessed through the Backend API.

Version 1 is a **read-only API** for the frontend. Scholarship records are managed internally by the automated backend pipeline:

**Scheduler → Source Connector → Keyword & URL Filter → Raw Data Collector → AI Extraction Module → Validator → Duplicate Checker → Database**

---

# Base URL

```
http://localhost:8000/api/v1
```

---

# Data Model

Every scholarship returned by the API follows the same structure.

```json
{
    "id": "uuid",
    "source_id": "uuid",
    "title": "Tsinghua University Scholarship",
    "university": "Tsinghua University",
    "country": "China",
    "degree": "Master's",
    "field": "Software Engineering",
    "funding": "Fully Funded",
    "deadline": "2027-03-31",
    "application_link": "https://...",
    "source_url": "https://...",
    "requirements": [
        "Bachelor's Degree",
        "English Proficiency"
    ],
    "documents_required": [
        "Passport",
        "Transcript",
        "Recommendation Letters"
    ],
    "ai_summary": "Scholarship for international Master's students in Software Engineering.",
    "status": "Open",
    "last_verified": "2026-07-28T15:00:00Z",
    "created_at": "2026-07-28T15:00:00Z",
    "updated_at": "2026-07-28T15:00:00Z"
}
```

---

# Endpoints

## GET /scholarships

Returns a paginated list of scholarships.

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| page | Integer | Page number (default: 1) |
| limit | Integer | Results per page (default: 20) |
| country | String | Filter by country |
| degree | String | Filter by degree |
| field | String | Filter by field |
| status | String | Filter by scholarship status |
| search | String | Search by scholarship title or university |

### Example

```
GET /scholarships?page=1&limit=20
```

### Response

```json
{
    "page": 1,
    "limit": 20,
    "total": 145,
    "data": [
        {
            "...": "..."
        }
    ]
}
```

---

## GET /scholarships/{id}

Returns detailed information about a single scholarship.

### Example

```
GET /scholarships/550e8400-e29b-41d4-a716-446655440000
```

### Response

```json
{
    "...": "..."
}
```

---

## GET /health

Returns the current health status of the backend.

### Response

```json
{
    "status": "healthy"
}
```

---

# Error Responses

If an error occurs, the API always returns a consistent error format.

```json
{
    "error": {
        "code": 404,
        "message": "Scholarship not found"
    }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

# Response Standards

- All responses are returned in JSON.
- Dates and timestamps use ISO 8601 format.
- UUIDs are used as resource identifiers.
- Pagination is supported for list endpoints.
- Filtering and searching are performed by the backend.
- The frontend should remain free of business logic whenever possible.

---

# Future Endpoints

The following endpoints are planned for future versions but are **not required for Version 1**.

```
GET /sources

GET /sources/{id}

GET /profile

PUT /profile

GET /notifications

GET /statistics
```

---

# Version 1 Scope

The API supports:

- Viewing scholarships
- Viewing scholarship details
- Filtering scholarship results
- Searching scholarships
- Backend health check

Scholarship records are managed exclusively by the automated backend pipeline. The frontend is read-only during Version 1.

---

# API Design Principles

The API follows these design principles:

- RESTful endpoint design.
- Stateless communication.
- Consistent request and response formats.
- JSON used for all data exchange.
- Pagination for collection endpoints.
- ISO 8601 timestamps.
- UUIDs as primary resource identifiers.
- Backward compatibility whenever possible for future API versions.