# Technology Stack

## Overview

ScholarScout AI is built using a modern, lightweight technology stack that emphasizes simplicity, maintainability, and scalability.

Version 1 focuses on reliability and rapid development rather than supporting large-scale production workloads.

---

# Frontend

## Framework

- Next.js

## Language

- TypeScript

## Styling

- Tailwind CSS

## State Management

- React Hooks

## Data Fetching

- Fetch API

---

# Backend

## Framework

- FastAPI

## Language

- Python 3.12+

## API Style

- REST API

## Data Validation

- Pydantic

---

# Database

## Database

- PostgreSQL

## ORM

- SQLAlchemy

## Migrations

- Alembic

---

# AI

## Provider

- OpenAI API

## Purpose

- Extract structured scholarship information from webpages.
- Generate scholarship summaries.

---

# Web Scraping

## Libraries

- Playwright
- BeautifulSoup4

## Purpose

- Visit websites.
- Download webpages.
- Parse HTML.
- Extract webpage content.

---

# Scheduler

## Library

- APScheduler

Purpose:

- Execute the scholarship discovery pipeline automatically.

---

# Raw Data Storage

Version 1 stores downloaded webpages on the local filesystem.

Example:

storage/raw_pages/

---

# API

- REST
- JSON
- ISO 8601 timestamps
- UUID identifiers

---

# Development Tools

- Git
- GitHub
- VS Code

---

# Future Technologies

Future versions may introduce:

- Docker
- Redis
- Celery
- S3-compatible storage
- Kubernetes
- Cloud deployment

---

# Design Principles

The chosen technologies should:

- Be easy to learn.
- Be well documented.
- Support modular development.
- Support future scalability.
- Avoid unnecessary complexity during Version 1.