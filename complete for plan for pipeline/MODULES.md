# Modules

## Overview

ScholarScout AI is built as a collection of independent modules.

Each module has a single responsibility and communicates with the next module through well-defined inputs and outputs.

A module should only perform its own task and should never contain business logic that belongs to another module.

This modular design makes the system easier to develop, test, maintain, and extend with new scholarship sources.

---

# System Workflow

```
Scheduler
    │
    ▼
Source Connector
    │
    ▼
Keyword & URL Filter
    │
    ▼
Raw Data Collector
    │
    ▼
AI Extraction Module
    │
    ▼
Validator
    │
    ▼
Duplicate Checker
    │
    ▼
Database
    │
    ▼
Backend API
    │
    ▼
Dashboard
```

---

# Module Responsibilities

## 1. Scheduler

### Purpose

Starts the scholarship discovery pipeline automatically.

### Responsibilities

- Run the pipeline at scheduled intervals.
- Trigger the Source Connector.
- Record execution history.

### Input

None

### Output

Pipeline execution request

### Does NOT

- Visit websites.
- Process scholarship information.
- Store scholarship data.

---

## 2. Source Connector

### Purpose

Collect webpages from configured scholarship sources.

Version 1 supports:

- Official Chinese university websites

Future versions may support:

- CSC
- Google Search
- Facebook
- Telegram
- Scholarship Portals

### Responsibilities

- Visit configured websites.
- Discover webpages.
- Download webpage content.
- Pass downloaded pages to the Keyword & URL Filter.

### Input

Scheduler

### Output

Downloaded webpages

### Does NOT

- Extract scholarship information.
- Call AI.
- Validate information.
- Store data.

---

## 3. Keyword & URL Filter

### Purpose

Reduce unnecessary AI processing by filtering irrelevant webpages.

### Responsibilities

- Inspect webpage URLs.
- Inspect page titles.
- Inspect headings.
- Match scholarship-related keywords.
- Forward only relevant pages.

Example keywords:

- scholarship
- admission
- graduate
- masters
- international
- funding
- financial aid
- application

### Input

Downloaded webpages

### Output

Filtered scholarship-related webpages

### Does NOT

- Download webpages.
- Extract scholarship information.
- Store data.

---

## 4. Raw Data Collector

### Purpose

Store downloaded webpages before AI processing.

### Responsibilities

- Save raw HTML or Markdown.
- Organize pages by source.
- Allow pages to be reprocessed later.

### Input

Filtered webpages

### Output

Stored raw pages

### Does NOT

- Modify webpage content.
- Extract scholarship information.
- Validate data.

---

## 5. AI Extraction Module

### Purpose

Convert raw webpages into structured scholarship information.

### Responsibilities

Extract:

- Scholarship title
- University
- Country
- Degree
- Field
- Funding
- Deadline
- Requirements
- Required documents
- Application link
- AI summary

### Input

Stored raw page

### Output

Structured scholarship object

### Does NOT

- Visit websites.
- Store data.
- Validate information.

---

## 6. Validator

### Purpose

Verify extracted scholarship information before storage.

### Responsibilities

Validate:

- Required fields
- Application deadline
- Application link
- University name
- Supported country

### Input

Structured scholarship object

### Output

Validated scholarship object

### Does NOT

- Visit websites.
- Call AI.
- Store data.

---

## 7. Duplicate Checker

### Purpose

Prevent duplicate scholarship records.

### Responsibilities

Compare scholarships using:

- Application link
- Scholarship title
- University
- Source URL

If a scholarship already exists:

- Update the existing record.

Otherwise:

- Create a new scholarship record.

### Input

Validated scholarship object

### Output

Verified scholarship object

### Does NOT

- Visit websites.
- Call AI.

---

## 8. Database

### Purpose

Store verified scholarship information.

### Responsibilities

Store:

- Scholarships
- Sources
- Search Logs
- User Profile

### Input

Verified scholarship object

### Output

Persistent scholarship records

### Does NOT

- Process webpages.
- Call AI.
- Perform scraping.

---

## 9. Backend API

### Purpose

Provide scholarship information to the frontend.

### Responsibilities

- Return scholarship list.
- Return scholarship details.
- Return health status.

### Input

Database queries

### Output

JSON responses

### Does NOT

- Visit websites.
- Call AI.
- Perform scraping.

---

## 10. Dashboard

### Purpose

Display scholarship information to the user.

### Responsibilities

- Display scholarship list.
- Display scholarship details.
- Search scholarships.
- Filter scholarships.

### Input

Backend API responses

### Output

User interface

### Does NOT

- Access the database directly.
- Call AI.
- Download webpages.

---

# Communication Between Modules

Every module communicates through well-defined inputs and outputs.

Each module performs one responsibility before passing its result to the next module.

Modules should never depend on another module's internal implementation.

This design allows modules to be developed, tested, and replaced independently.

---

# Development Ownership

## Frontend

Responsible for:

- Dashboard
- User Interface
- Backend API integration

---

## Backend

Responsible for:

- Scheduler
- Source Connector
- Keyword & URL Filter
- Raw Data Collector
- AI Extraction Module
- Validator
- Duplicate Checker

---

## Shared

Responsible for:

- Database schema
- API contract
- Documentation
- Overall architecture

---

# Design Principles

The module design follows these principles:

- Single Responsibility Principle
- Separation of Concerns
- Loose Coupling
- Modular Architecture
- Scalability
- Maintainability