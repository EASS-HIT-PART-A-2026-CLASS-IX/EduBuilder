# EduBuilder — local no-Docker updates

Replace the files in this bundle on top of your repository.

## What changed
- `poseai_backend/main.py`
  - Redis is now optional.
  - If `DISABLE_REDIS=1`, the API runs fully without Redis.
  - If Redis is not available, the API falls back automatically instead of hanging.

- `scripts/capture_trace_excerpt.py`
  - No longer depends on Docker or Redis monitor.
  - Captures a simple local HTTP trace from the running API.

- `docs/EX3-notes.md`
  - Uses a simple placeholder for the local trace excerpt.

## Recommended local EX3 run (no Docker)

### PowerShell
```powershell
$env:DISABLE_REDIS="1"
uv run python -m scripts.migrate
uv run uvicorn poseai_backend.main:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal:
```powershell
uv run streamlit run frontend/app.py
```

To inject the trace excerpt:
```powershell
$env:DISABLE_REDIS="1"
uv run python scripts/capture_trace_excerpt.py
```

## Important
Keep your existing `compose.yaml` in the repo for the assignment.
You just do not need Docker for everyday local development anymore.
