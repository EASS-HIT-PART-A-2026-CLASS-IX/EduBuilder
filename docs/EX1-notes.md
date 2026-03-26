# EX1 Notes – EduBuilder Backend

This file is for presenting **EX1 separately** from the richer EX3 system.

## Goal
Show a clean FastAPI backend for one core resource: `Course`.

## File to run
Use:

```bash
uv run uvicorn backend.main_ex1:app --reload
```

## What this version includes
- FastAPI backend
- One core resource: `Course`
- CRUD endpoints:
  - `GET /courses`
  - `GET /courses/{course_id}`
  - `POST /courses`
  - `PUT /courses/{course_id}`
  - `DELETE /courses/{course_id}`
- Health endpoint: `GET /health`
- No authentication
- Simple in-memory data store
- Pytest coverage for the happy-path CRUD flow

## Tests
Run:

```bash
uv run pytest tests/test_ex1_api.py
```

## Why this file exists
The full project later evolved into EX3 and includes authentication, Redis, worker flows, and AI features.

For the EX1 presentation, this file keeps the scope exactly on the backend foundations.
