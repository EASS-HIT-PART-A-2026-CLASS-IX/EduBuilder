# EX1 Notes – EduBuilder Backend

This file presents **EX1 separately** from the richer EX3 system.

## Goal
Ship a small FastAPI backend for one core resource: `Plan`.

## Files used for EX1
- `poseai_backend/main_ex1.py`
- `tests/test_ex1_api.py`
- `docs/EX1-notes.md`

## What this version includes
- FastAPI backend
- one core resource: `Plan`
- in-memory data layer
- CRUD endpoints
- Pydantic validation
- pytest coverage using FastAPI `TestClient`
- no authentication
- local run instructions for the API and tests

## Create the local environment with uv
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

On Windows PowerShell:
```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Run the EX1 API
```bash
uv run uvicorn poseai_backend.main_ex1:app --reload
```

## Run the EX1 tests
```bash
uv run pytest tests/test_ex1_api.py -q
```

## Notes
This EX1 version intentionally stays simple and local:
- no database
- no JWT
- no roles
- no background worker

SQLite, migrations, and authentication are introduced later in EX3.
