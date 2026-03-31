# EduBuilder - EX1 to EX3 Submission

EduBuilder is a small, local-first product built around one consistent domain: **learning plans**. The same domain is reused through EX1, EX2, and EX3 so the repository can be graded as one incremental product.

## Quick setup

### Create the `uv` environment

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

## Exercise map

### EX1 - FastAPI Foundations

Main files:

- `poseai_backend/main_ex1.py`
- `tests/test_ex1_api.py`
- `docs/EX1-notes.md`

Run EX1:

```bash
uv run uvicorn poseai_backend.main_ex1:app --reload
uv run pytest tests/test_ex1_api.py -q
```

EX1 delivers:

- FastAPI CRUD for one core resource: `Plan`
- in-memory data layer
- Pydantic validation
- pytest coverage with FastAPI `TestClient`
- clear local run instructions

### EX2 - Friendly Interface

Main files:

- `frontend/app_ex2.py`
- `poseai_backend/main_ex1.py`
- `docs/EX2-notes.md`
- `tests/test_ex2_ui.py`

Run EX2:

```bash
uv run uvicorn poseai_backend.main_ex1:app --reload
uv run streamlit run frontend/app_ex2.py
```

EX2 delivers:

- Streamlit interface over the EX1 `/plans` API
- no authentication or security prompts
- list existing entries immediately
- add a new entry through a lightweight chat-style flow
- one small extra: summary metrics and CSV export
- automated EX2 coverage for the prompt-to-plan flow and CSV export

### EX3 - Full-Stack Microservices Final Project

Main files:

- `poseai_backend/main.py`
- `poseai_backend/auth.py`
- `poseai_backend/database.py`
- `poseai_backend/models.py`
- `frontend/app.py`
- `scripts/refresh.py`
- `scripts/migrate.py`
- `scripts/seed.py`
- `scripts/demo.sh`
- `scripts/capture_trace_excerpt.py`
- `docs/EX3-notes.md`
- `docs/runbooks/compose.md`
- `compose.yaml`
- `alembic/`
- `tests/test_api.py`
- `tests/test_worker.py`
- `tests/test_openapi.py`
- `.github/workflows/ci.yml`

Run EX3 locally:

```bash
uv run python -m scripts.migrate
uv run python -m scripts.seed
uv run uvicorn poseai_backend.main:app --reload
uv run streamlit run frontend/app.py
```

Run EX3 with Docker Compose:

```bash
docker compose up --build
```

EX3 delivers:

- FastAPI backend with SQLite persistence through SQLModel
- Alembic migrations and seed script
- Streamlit interface with chat-style course creation, My Courses, Shared Courses, and Admin Panel
- Redis-backed rate limiting
- async refresh worker with retries and idempotency
- JWT authentication and admin role checks
- automated tests including worker and OpenAPI coverage
- Docker Compose orchestration for API, frontend, Redis, and worker
- one enhancement: weekly learning-plan digest generation

## Domain model

The core resource is a **learning plan**.

Core fields:

- `title`
- `goal`
- `cues`
- `level`
- `is_public`

EX3 adds:

- `owner`
- `weekly_digest`

## AI Assistance

AI tools were used as pair-programming aids for code structure, debugging, tests, and documentation. Outputs were reviewed, edited, and verified locally before submission.
