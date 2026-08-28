# Project Folder Structure

## Overview

The project is divided into two independent applications:

- Backend
- Frontend

Each application has its own responsibilities.

---

# Root Structure

```
ScholarScout-AI/
│
├── backend/
├── frontend/
├── docs/
└── README.md
```

---

# Backend

```
backend/
│
├── app/
│   │
│   ├── api/
│   │
│   ├── config/
│   │
│   ├── database/
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │     │
│   │     ├── scheduler/
│   │     ├── connectors/
│   │     ├── filters/
│   │     ├── collector/
│   │     ├── extraction/
│   │     ├── validator/
│   │     └── duplicate_checker/
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── storage/
│     └── raw_pages/
│
├── migrations/
│
├── tests/
│
├── requirements.txt
│
└── .env
```

---

# Frontend

```
frontend/
│
├── app/
│
├── components/
│
├── lib/
│
├── services/
│
├── types/
│
├── public/
│
└── package.json
```

---

# Documentation

```
docs/
│
├── README.md
├── PROJECT_SCOPE.md
├── ARCHITECTURE.md
├── MODULES.md
├── DATABASE.md
├── API.md
├── ROADMAP.md
├── TECH_STACK.md
├── FOLDER_STRUCTURE.md
├── CODING_GUIDELINES.md
└── AI_CONTEXT.md
```

---

# Folder Responsibilities

## Backend

Contains:

- Database
- API
- Scheduler
- Source Connector
- Keyword & URL Filter
- Raw Data Collector
- AI Extraction
- Validator
- Duplicate Checker

---

## Frontend

Contains:

- Dashboard
- UI Components
- API Communication

---

## Docs

Contains all project documentation.

---

# Design Principles

- Keep modules independent.
- Keep files organized by responsibility.
- Avoid deeply nested folders.
- Make navigation easy for both developers and AI assistants.