# EX1 Notes – EduBuilder Backend

This file presents **EX1 separately** from the richer EX3 system.

## Goal
Show a clean FastAPI backend for one core resource: `Plan`.

## Files used for EX1
- `poseai_backend/main_ex1.py`
- `tests/test_ex1_api.py`

## Run the API
```bash
uv run uvicorn poseai_backend.main_ex1:app --reload
```

## What this version includes
- FastAPI backend
- one core resource: `Plan`
- CRUD endpoints
- health endpoint
- no authentication
- simple in-memory data store
- pytest coverage for the happy-path CRUD flow
