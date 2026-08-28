# System Architecture

## Overview

ScholarScout AI is a modular scholarship discovery system designed to automate the process of finding scholarship opportunities.

Instead of building one large AI agent, the system is divided into independent modules. Each module has a single responsibility and communicates with the next module through a well-defined workflow.

Version 1 focuses on discovering scholarships from official Chinese university websites only. The architecture, however, is designed so that additional scholarship sources and countries can be added in the future without major changes.

---

# Version 1 Architecture

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

# System Workflow

The complete scholarship discovery process follows these steps:

1. The Scheduler starts the pipeline at a configured interval.
2. The Source Connector visits official Chinese university websites.
3. The Keyword & URL Filter keeps only pages that are likely to contain scholarship information.
4. The Raw Data Collector stores the downloaded pages for future processing.
5. The AI Extraction Module converts the raw pages into structured scholarship information.
6. The Validator verifies that the extracted information is complete and valid.
7. The Duplicate Checker prevents duplicate scholarship records from being stored.
8. The Database stores verified scholarship information.
9. The Backend API provides scholarship data to the dashboard.
10. The Dashboard displays scholarship information to the user.

---

# Module Responsibilities

## 1. Scheduler

### Purpose

Starts the scholarship discovery process automatically.

### Responsibilities

- Run the pipeline at scheduled intervals.
- Trigger the Source Connector.
- Record execution times and status.

### Does NOT

- Visit websites.
- Process scholarship information.
- Store data.

---

## 2. Source Connector

### Purpose

Collect scholarship-related pages from a configured source.

Version 1 supports:

- Official Chinese university websites

Future versions may support:

- CSC
- Facebook
- Google Search
- Telegram
- Scholarship Portals

### Responsibilities

- Visit configured university websites.
- Discover pages that may contain scholarship information.
- Download webpage content.
- Send downloaded pages to the Keyword & URL Filter.

### Does NOT

- Call AI.
- Validate information.
- Save scholarships to the database.

---

## 3. Keyword & URL Filter

### Purpose

Reduce unnecessary AI processing by filtering irrelevant pages.

### Responsibilities

Keep only pages that are likely to contain scholarship information.

Examples include pages containing keywords such as:

- scholarship
- admission
- admissions
- graduate
- masters
- international
- funding
- financial aid
- apply
- application

The filtering may use:

- URL
- Page title
- Page headings

### Does NOT

- Extract scholarship information.
- Call AI.
- Store data.

---

## 4. Raw Data Collector

### Purpose

Store downloaded pages before AI processing.

### Responsibilities

- Store raw HTML or Markdown.
- Organize downloaded pages by source.
- Allow pages to be processed again later.

### Does NOT

- Modify downloaded content.
- Extract scholarship information.
- Save data to the database.

---

## 5. AI Extraction Module

### Purpose

Convert raw pages into structured scholarship information.

### Responsibilities

Extract information such as:

- Scholarship Title
- University
- Country
- Degree
- Field
- Funding
- Deadline
- Requirements
- Required Documents
- Application Link
- Scholarship Summary

Output should always follow the project's standardized scholarship object.

### Does NOT

- Visit websites.
- Validate information.
- Save data.

---

## 6. Validator

### Purpose

Verify extracted scholarship information before it is stored.

### Responsibilities

Check:

- Required fields exist.
- Deadline is valid.
- Application link exists.
- Country is supported.
- University name is present.

Invalid records should not continue through the pipeline.

### Does NOT

- Visit websites.
- Call AI.
- Save data.

---

## 7. Duplicate Checker

### Purpose

Prevent duplicate scholarship records.

### Responsibilities

Compare scholarships using:

- Application Link
- Scholarship Title
- University
- Deadline

If a scholarship already exists:

- Update the existing record.

Otherwise:

- Create a new record.

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
- User Profile
- Source Information
- Search Logs

The database is the single source of truth for the application.

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
- Return system status.

The API is the only way the frontend accesses data.

### Does NOT

- Access websites.
- Call AI.
- Perform business logic.

---

## 10. Dashboard

### Purpose

Display scholarship information.

Version 1 keeps the dashboard intentionally simple.

### Responsibilities

- Display scholarship list.
- View scholarship details.
- Search scholarships.
- Filter scholarships.

### Does NOT

- Access the database directly.
- Call AI.
- Perform scraping.

---

# Data Flow

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

# Scalability

Although Version 1 only supports official Chinese university websites, the architecture is designed to support additional sources in the future.

Examples include:

- CSC Connector
- Google Search Connector
- Facebook Connector
- Telegram Connector
- Scholarship Portal Connector

Each new connector should produce the same output expected by the rest of the pipeline.

No changes should be required to the AI Extraction Module, Validator, Database, API, or Dashboard when new connectors are added.

---

# Design Principles

The architecture follows these principles:

- Single Responsibility Principle: every module performs one task only.
- Modular Design: modules can be developed and tested independently.
- Scalability: new countries and sources can be added without redesigning the system.
- Maintainability: each module can be modified without affecting unrelated modules.
- Separation of Concerns: data collection, AI processing, validation, storage, and presentation remain independent.