# EX3 Notes - EduBuilder

## 1. Final EX3 shape

EduBuilder is the final EX3 submission of a small, local-first learning-plan product.
It keeps one narrow domain across the course exercises and combines:

- a FastAPI backend
- SQLite persistence through SQLModel
- a Streamlit frontend
- Redis support for rate limiting and worker coordination
- an async background worker for digest generation

## 2. Services in the local architecture

### API service

Implemented in `poseai_backend/main.py`.

Responsibilities:

- register and login users
- issue JWT access tokens
- expose public plan browsing routes
- expose authenticated plan-management routes
- expose admin-only routes
- return health information
- include rate-limit headers when Redis is available

### Persistence layer

Implemented with SQLite + SQLModel + Alembic.

Responsibilities:

- persist users and plans locally
- keep the schema reproducible through migrations
- allow clean local setup without committing a database artifact

### Frontend service

Implemented in `frontend/app.py`.

Responsibilities:

- browse shared plans quickly
- register and sign in
- create, edit, and delete personal plans through the backend
- keep the user flow simple enough for a short demo
- preserve the chat-style course creation experience

### Worker service

Implemented in `scripts/refresh.py`.

Responsibilities:

- scan public plans
- generate a weekly digest
- retry transient failures
- prevent duplicate work with Redis-backed idempotency keys
- keep concurrency bounded

## 3. Compose orchestration

The repository includes `compose.yaml` with these cooperating services:

- `api`
- `frontend`
- `redis`
- `worker`

This satisfies the EX3 requirement for a local multi-service stack launched with Docker Compose.

## 4. Async refresher deliverable

The async refresher is implemented in `scripts/refresh.py`.

It includes:

- bounded concurrency via `anyio.CapacityLimiter`
- retry handling for transient failures
- Redis-backed idempotency keys
- worker settings through environment variables
- automated coverage with a `pytest.mark.anyio` worker test

## 5. Security baseline

The EX3 security baseline in this project includes:

- hashed credentials
- JWT-protected create, update, and delete plan flows
- role-aware authorization for admin-only endpoints
- tests that cover expired tokens
- tests that cover missing scope and missing permissions

### JWT secret rotation steps

1. Generate a new local value for `JWT_SECRET_KEY`.
2. Update `.env` or the Compose environment override.
3. Restart the API service.
4. Re-login so previously issued tokens are replaced.
5. Re-run the auth-related tests if needed.

## 6. Enhancement

The EX3 enhancement is the weekly learning-plan digest generated for public plans by the background worker.

## 7. Automated verification

Main verification assets in the repository:

- `tests/test_api.py`
- `tests/test_worker.py`
- `tests/test_openapi.py`
- `.github/workflows/ci.yml`

## 8. Demo flow

The local demo entry point is:

```bash
uv run python -m scripts.migrate
uv run python scripts/seed.py
uv run uvicorn poseai_backend.main:app --reload
uv run streamlit run frontend/app.py
```

## 9. Trace excerpt

The block below is intended to be refreshed locally with `uv run python scripts/capture_trace_excerpt.py`.
It now records both the HTTP health checks and a small Redis trace tied to the worker/idempotency flow.

<!-- TRACE_EXCERPT_START -->
```text
# local-redis-trace
GET /health -> 200
GET /plans -> 200
GET /plans/shared -> 200
REDIS PING -> True
REDIS SETEX trace:edubuilder:demo -> OK
REDIS GET trace:edubuilder:demo -> worker-idempotency-ok
```
<!-- TRACE_EXCERPT_END -->

## 10. Notes for the grader

EduBuilder is intentionally local-first and limited in scope.
The goal is not production deployment, but a tidy demonstration of:

- backend + persistence + frontend integration
- one additional background microservice
- basic local security controls
- automated tests
- reproducible local setup
