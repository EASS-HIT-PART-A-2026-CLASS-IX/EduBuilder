# EX3 Notes – EduBuilder

## 1. Final EX3 shape
EduBuilder completes the EX1–EX3 progression as a tidy, local-first **learning-plan catalog** that combines:

- a FastAPI backend,
- SQLite persistence through SQLModel,
- a Streamlit user interface,
- Redis for rate limiting and worker coordination,
- and an async worker for background digest generation.

## 2. Services in the local architecture

### 2.1 API service
Implemented in `poseai_backend/main.py`.

Responsibilities:

- authentication and authorization,
- plan CRUD,
- public/shared plan browsing,
- personal plan management,
- admin-only routes,
- health checks,
- Redis-backed rate-limit headers.

### 2.2 Persistence layer
Implemented with SQLite, SQLModel, and Alembic migrations.

### 2.3 Frontend service
Implemented in `frontend/app.py`.

Responsibilities:

- browse shared plans immediately,
- sign in or register,
- create and edit plans through the backend API,
- keep the main flows simple enough to demonstrate quickly.

### 2.4 Redis service
Redis is used for two focused EX3 tasks:

- API rate limiting,
- worker idempotency.

### 2.5 Worker service
Implemented in `scripts/refresh.py`.

Responsibilities:

- scan public plans,
- generate a weekly digest,
- retry transient failures,
- prevent duplicate work through Redis-backed idempotency keys,
- keep concurrency bounded.

## 3. Compose orchestration
The project includes `compose.yaml` with these services:

- `api`
- `frontend`
- `redis`
- `worker`

## 4. Verification steps

### 4.1 Health endpoint
```bash
curl http://localhost:8000/health

### 4.2 Rate-limit headers
```bash
curl -i http://localhost:8000/plans
```

### 4.3 Frontend reachability
Open `http://localhost:8501`

## 5. Testing
```bash
uv run pytest
```

## 6. Async refresher deliverable
The async refresher is implemented in `scripts/refresh.py` and provides:

- bounded concurrency via `anyio.CapacityLimiter`,
- retries for transient failures,
- Redis-backed idempotency keys,
- a `pytest.mark.anyio` worker test.

## 7. Security baseline
The project includes:

- hashed credentials,
- JWT-protected create/edit/delete flows,
- role/scope checks for admin-only endpoints,
- tests for expired tokens,
- tests for missing required scope.

## 8. Enhancement
The EX3 enhancement is a **weekly learning-plan digest** generated for public plans by the background worker.

## 9. Trace excerpt
I did not fabricate a “real” local Redis excerpt here. Before submission, run the helper below on your machine so this file contains an actual excerpt from your stack:

```bash
uv run python scripts/capture_trace_excerpt.py
```

After you run it locally, replace this section with the generated block.

<!-- TRACE_EXCERPT_START -->

```text
Run locally before submission:
uv run python scripts/capture_trace_excerpt.py
```

<!-- TRACE_EXCERPT_END -->
