# Development Roadmap

## Goal

Build a fully functional scholarship discovery system that automatically finds, validates, stores, and displays scholarship opportunities from official Chinese university websites.

The project will be developed in small, independent phases. Each phase produces a working component before moving to the next, making the system easier to develop, test, and maintain.

---

# Phase 1 – Project Setup ✅

## Objectives

* Create GitHub repository
* Define project architecture
* Design database
* Define API
* Prepare project folder structure
* Complete project documentation

## Deliverables

* README.md
* PROJECT_SCOPE.md
* ARCHITECTURE.md
* DATABASE.md
* API.md
* ROADMAP.md
* MODULES.md

**Status:** Completed

---

# Phase 2 – Backend Foundation

## Objectives

* Set up FastAPI project
* Configure PostgreSQL database
* Create database models
* Create database migrations
* Establish database connection
* Create initial API structure

## Deliverables

* Running FastAPI server
* Connected PostgreSQL database
* Database models
* Migration system
* Initial API endpoints

**Status:** Pending

---

# Phase 3 – Source Connector ✅

## Objectives

Build the first Source Connector for Version 1.

Responsibilities:

* Visit official Chinese university websites
* Discover scholarship-related pages
* Apply Keyword & URL Filter
* Download webpage content
* Store raw pages for future processing

Initially, only one university is required.

## Deliverables

* Working Source Connector
* Keyword & URL Filter
* Raw Data Collector
* Stored raw webpages
* PDF link discovery
* PDF downloading and text extraction
* PDF processing

**Status:** Completed

---

# Phase 4 – AI Extraction Module ✅

## Objectives

Extract structured scholarship information from the downloaded webpages.

Responsibilities:

* Read raw pages
* Extract scholarship information using AI
* Produce standardized scholarship objects

## Deliverables

* Working AI Extraction Module
* Standardized scholarship object
* Structured scholarship output
* Gemini-based scholarship extraction
* PDF scholarship extraction
* PDF scholarship evidence extraction

**Status:** Completed

---

# Phase 5 – Validator ✅

## Objectives

Validate extracted scholarship information before storing it.

Validation includes:

* Required fields
* Valid application deadline
* Valid application link
* Supported country
* University name

## Deliverables

* Working Validator
* Validated scholarship objects
* PDF evidence validator
* Version 1 scope validation
* CSC exclusion validation
* Target computing-field validation

**Status:** Completed

---

# Phase 6 – Duplicate Checker

## Objectives

Prevent duplicate scholarship records from being stored.

Checks include:

* Existing application link
* Existing scholarship title
* Existing university
* Existing source URL

If a scholarship already exists, update it instead of creating a duplicate.

## Deliverables

* Working Duplicate Checker
* Automatic insert/update logic

**Status:** Pending

---

# Phase 7 – Dashboard

## Objectives

Develop a simple frontend dashboard for viewing scholarship information.

Responsibilities:

* Set up Next.js project
* Connect to Backend API
* Display scholarship list
* Display scholarship details
* Search scholarships
* Filter scholarships

Version 1 prioritizes functionality over appearance.

## Deliverables

* Working dashboard
* Scholarship list page
* Scholarship details page
* Search functionality
* Filtering functionality

**Status:** Pending

---

# Phase 8 – End-to-End Integration

## Objectives

Integrate every module into one complete workflow.

Pipeline:

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

## Deliverables

* Complete working Version 1 system
* Successfully processed scholarships
* End-to-end testing completed

**Status:** Pending

---

# Phase 9 – Automation

## Objectives

Automate the scholarship discovery pipeline.

Responsibilities:

* Configure Scheduler
* Run the pipeline automatically
* Support configurable execution intervals
* Log execution history
* Handle failures gracefully
* Retry failed executions where appropriate

Example schedule:

* Every 6 hours

## Deliverables

* Fully automated scholarship discovery system
* Scheduled execution
* Execution logs

**Status:** Pending

---

# Phase 10 – Future Enhancements

The following features are intentionally outside the scope of Version 1.

Possible future improvements include:

* Additional university sources
* CSC Connector
* Google Search Connector
* Facebook Connector
* Telegram Connector
* Additional countries
* Multiple users
* User authentication
* Saved scholarships
* Scholarship application tracking
* Email notifications
* AI-powered scholarship recommendations
* Daily scholarship reports
* Advanced analytics dashboard

---

# Version 1 Completion Criteria

Version 1 will be considered complete when the system can:

* Automatically scan at least one official Chinese university website.
* Discover scholarship-related webpages.
* Filter irrelevant pages using the Keyword & URL Filter.
* Store raw webpages.
* Extract structured scholarship information using AI.
* Validate extracted scholarship information.
* Prevent duplicate scholarship records.
* Store verified scholarships in the database.
* Provide scholarship data through the Backend API.
* Display scholarships in the dashboard.
* Search and filter scholarship results.
* Execute automatically on a configurable schedule.

---

# Development Principles

The roadmap follows these principles:

* Build one independent module at a time.
* Test every module before integrating it.
* Keep modules loosely coupled.
* Prioritize functionality over optimization during Version 1.
* Design every phase with future scalability in mind.
