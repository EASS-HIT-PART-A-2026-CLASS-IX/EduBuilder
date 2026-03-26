# EduBuilder

EduBuilder is a small, local-first **course builder and course catalog** built across **EX1–EX3** around one consistent domain: **courses**.

The repository intentionally preserves:
- a focused **EX1 backend**,
- a lightweight **EX2 frontend**,
- and the richer **EX3 full-stack version**.

This makes the project easy to grade exercise-by-exercise while still showing the final integrated product.

## Grader quick map

If you are grading by exercise, use these files:

### EX1 – FastAPI Foundations (Backend)
- `backend/main_ex1.py`
- `tests/test_ex1_api.py`
- `docs/EX1-notes.md`

What this EX1 version includes:
- FastAPI backend
- one core resource: `Course`
- CRUD endpoints
- Pydantic models
- simple in-memory storage
- pytest coverage for the happy-path CRUD flow
- no authentication

### EX2 – Friendly Interface (Frontend connected to Backend)
- `frontend/app_ex2.py`
- `backend/main_ex1.py` for the cleanest EX2 demo
- `docs/EX2-notes.md`

What this EX2 version includes:
- lightweight Streamlit interface
- lists existing courses immediately
- allows adding a new course in one screen
- no login or security prompts in the UI
- small extra: visible course count and CSV export

### EX3 – Full-Stack Microservices Final Project
- `backend/main.py`
- `frontend/app.py`
- `backend/database.py`
- `backend/models.py`
- `compose.yaml`
- `scripts/refresh.py`
- `docs/EX3-notes.md`
- `docs/runbooks/compose.md`
- `.github/workflows/ci.yml`

What this EX3 version includes:
- SQLite persistence via SQLModel and Alembic
- Streamlit frontend
- Redis-backed rate limiting and worker idempotency
- async worker for weekly digest generation
- JWT authentication and role/scope checks
- Docker Compose orchestration
- pytest + Schemathesis-based testing

## Repository layout

```text
EduBuilder/
├─ alembic/
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions/
├─ backend/
│  ├─ __init__.py
│  ├─ auth.py
│  ├─ database.py
│  ├─ main.py
│  ├─ main_ex1.py
│  └─ models.py
├─ docs/
│  ├─ EX1-notes.md
│  ├─ EX2-notes.md
│  ├─ EX3-notes.md
│  ├─ submission-status.md
│  └─ runbooks/
│     └─ compose.md
├─ frontend/
│  ├─ app.py
│  └─ app_ex2.py
├─ scripts/
│  ├─ capture_trace_excerpt.py
│  ├─ demo.sh
│  ├─ migrate.py
│  ├─ refresh.py
│  └─ seed.py
├─ tests/
│  ├─ conftest.py
│  ├─ test_api.py
│  ├─ test_ex1_api.py
│  ├─ test_openapi.py
│  └─ test_worker.py
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ .env.example
├─ .gitignore
├─ alembic.ini
├─ compose.yaml
├─ pyproject.toml
├─ requirements.txt
├─ uv.lock
└─ README.md
```

## Why the repository contains both simple and rich versions

The final EX3 application is naturally richer than EX1 and EX2. To keep grading clean and aligned with the assignment scope, the repository also preserves:
- a dedicated **EX1 backend** in `backend/main_ex1.py`, and
- a dedicated **EX2 frontend** in `frontend/app_ex2.py`.

So while the final product includes authentication, Redis, worker flows, and AI-assisted features, the earlier exercises can still be demonstrated in their intended minimal form.

## Domain continuity across EX1–EX3

The same domain is reused throughout all exercises: **courses / course catalog / course builder**.

That means:
- EX1 establishes the core backend resource (`Course`),
- EX2 adds a lightweight interface for that same resource,
- EX3 extends the same product into a local multi-service system.

## Local setup

### Create the environment

```bash
uv venv
uv sync
```

## How to run EX1

```bash
uv run uvicorn backend.main_ex1:app --reload
```

EX1 URLs:
- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

Run the EX1 tests:

```bash
uv run pytest tests/test_ex1_api.py
```

## How to run EX2

Start the EX1 API first, then launch the lightweight frontend:

```bash
uv run uvicorn backend.main_ex1:app --reload
uv run streamlit run frontend/app_ex2.py
```

EX2 URLs:
- API: `http://127.0.0.1:8000`
- Streamlit: `http://127.0.0.1:8501`

## How to run EX3 locally with uv

Apply migrations:

```bash
uv run python -m scripts.migrate
```

Run the backend:

```bash
uv run uvicorn backend.main:app --reload
```

Run the frontend in a second terminal:

```bash
uv run streamlit run frontend/app.py
```

Optional seed data:

```bash
uv run python scripts/seed.py
```

## How to run EX3 with Docker Compose

```bash
docker compose up --build
```

Services:
- API: `http://localhost:8000`
- Frontend: `http://localhost:8501`
- Redis: `localhost:6379`
- Worker: background process inside the Compose stack

The API and worker both apply Alembic migrations before starting.

To stop everything:

```bash
docker compose down
```

## EX3 required pieces covered

The EX3 implementation includes:
- one Git repository for the whole project,
- FastAPI backend,
- SQLite/SQLModel persistence,
- Streamlit user-facing interface,
- Redis service,
- async worker service,
- `compose.yaml`,
- Compose runbook in `docs/runbooks/compose.md`,
- async refresh logic in `scripts/refresh.py`,
- worker tests using `pytest.mark.anyio`,
- JWT-protected routes and role checks,
- tests for expired tokens and missing scope,
- a bounded-scope enhancement: weekly digest generation,
- a local demo script: `bash scripts/demo.sh`,
- CI running migrations, pytest, and Schemathesis contract tests.

## Tests

Run all tests:

```bash
uv run pytest
```

Run only EX1 tests:

```bash
uv run pytest tests/test_ex1_api.py
```

Run only EX3 API tests:

```bash
uv run pytest tests/test_api.py
```

Run only worker tests:

```bash
uv run pytest tests/test_worker.py
```

Run only contract tests:

```bash
uv run pytest tests/test_openapi.py
```

## Demo flow for graders

A simple local demo script is included:

```bash
bash scripts/demo.sh
```

Suggested grading flow for EX3:
1. Start the stack.
2. Open `/health` and `/docs`.
3. Open the Streamlit frontend.
4. Browse shared courses anonymously.
5. Register a user and create a private course.
6. Share that course and verify that it appears in the public catalog.
7. Check an admin-only route.
8. Inspect worker behavior and Redis-backed processing.

## Security baseline (EX3)

- Passwords are hashed with `passlib`.
- Access is controlled with Bearer JWTs.
- Protected create/edit/delete flows require authentication.
- Role/scope checks are enforced on admin-only endpoints.
- Expired-token and missing-scope scenarios are covered by tests.
- Sensitive values belong in `.env`, not in source control.

## Persistence and reproducibility

- Persistence is local SQLite through SQLModel.
- Schema setup is reproducible through Alembic migrations.
- `scripts/seed.py` provides reproducible starter data.
- SQLite artifacts are not meant to be committed.

## AI assistance

AI tools were used as pair-programming aids for:
- refining the FastAPI route structure,
- improving test coverage,
- tightening documentation,
- clarifying Docker Compose orchestration,
- validating that the final local workflow matched the assignment brief.

All generated suggestions were manually reviewed, edited, and verified locally.

## Submission hygiene

Before submission, verify that the repository or ZIP does **not** include:
- `.env`
- `.venv/`
- `venv/`
- `.pytest_cache/`
- `.hypothesis/`
- `app.db`
- other SQLite artifacts

## Manual checks outside the codebase

These items cannot be proven from code alone and must still be confirmed manually:
- AWS Academy prerequisite completion
- whether a bonus screen capture was recorded
- whether the correct GitHub Classroom repository was used
- whether required Git tags were created
