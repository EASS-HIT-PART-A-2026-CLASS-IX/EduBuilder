# Docker Compose Runbook

## Purpose

This runbook explains how to launch, verify, and stop the local EX3 stack for EduBuilder.
The stack contains:

- `api`
- `frontend`
- `redis`
- `worker`

## Compose launch

From the repository root:

```bash
docker compose up --build
```

## No-Docker local development

For daily development on a laptop, you can also run the API without Docker and without Redis by setting:

```powershell
$env:DISABLE_REDIS="1"
```

Then run:

```powershell
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
