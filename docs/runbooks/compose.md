# Docker Compose Runbook

## Purpose

This runbook explains how to launch, verify, and stop the local EX3 stack for EduBuilder.

## Services

The stack contains:

- `api` on `http://localhost:8000`
- `frontend` on `http://localhost:8501`
- `redis` on `localhost:6379`
- `worker` for the async weekly-digest refresh flow

## Compose launch

From the repository root:

```bash
docker compose up --build
```

## No-Docker local development

For daily development on a laptop, you can also run the API without Docker and without Redis:

```powershell
$env:DISABLE_REDIS="1"
uv run python -m scripts.migrate
uv run uvicorn poseai_backend.main:app --host 127.0.0.1 --port 8000 --reload
uv run streamlit run frontend/app.py
```

## Verify health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/plans
curl http://localhost:8000/plans/shared
```

Expected result:

- `/health` returns `200`
- `/plans` returns a JSON list
- `/plans/shared` returns a JSON list

## Verify rate-limit headers

When Redis is running, the API should return local rate-limit headers:

```bash
curl -i http://localhost:8000/plans
```

Look for:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`

## Verify the worker

Inspect the worker logs after the stack is up:

```bash
docker compose logs worker
```

You should see the worker start, process public plans, and write weekly digest values.

## Run migrations, pytest, and Schemathesis checks

From the repository root:

```bash
python -m scripts.migrate
pytest tests/test_api.py -q
pytest tests/test_worker.py -q
pytest tests/test_openapi.py -q
```

These are the same checks used in `.github/workflows/ci.yml`.

## Stop the stack

```bash
docker compose down -v
```
