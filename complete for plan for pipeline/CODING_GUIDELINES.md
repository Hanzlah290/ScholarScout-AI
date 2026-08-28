# Coding Guidelines

## Goal

Write clean, modular, maintainable code.

Every file should have one clear responsibility.

---

# General Principles

- Follow the Single Responsibility Principle.
- Keep modules independent.
- Avoid duplicate business logic.
- Prefer readability over clever code.
- Write self-explanatory code.

---

# Python

- Use Python 3.12+
- Use type hints.
- Use async functions where appropriate.
- Use descriptive function names.
- Use descriptive variable names.
- Add docstrings to public classes and functions.

---

# TypeScript

- Use strict typing.
- Avoid using any.
- Prefer interfaces for data models.
- Keep components small.

---

# API

- Follow REST principles.
- Return JSON.
- Use UUID identifiers.
- Return proper HTTP status codes.
- Keep response formats consistent.

---

# Database

- Never duplicate data unnecessarily.
- Use migrations for schema changes.
- Keep tables normalized.
- Use foreign keys appropriately.

---

# Error Handling

- Handle exceptions gracefully.
- Log meaningful error messages.
- Never silently ignore errors.

---

# Configuration

- Never hardcode URLs.
- Never hardcode API keys.
- Store configuration in environment variables.
- Read runtime settings from configuration files where appropriate.

---

# Project Structure

- One module, one responsibility.
- One folder per major feature.
- Separate business logic from API logic.
- Separate storage from processing.

---

# AI Guidelines

When generating code:

- Follow the project architecture.
- Do not bypass the Validator.
- Do not access the database directly from the frontend.
- Do not duplicate module responsibilities.
- Keep code modular.
- Generate production-quality code.

---

# Code Quality

Before considering code complete, ensure:

- It compiles.
- It follows the project architecture.
- It contains no unnecessary complexity.
- It is readable.
- It is easy to test.