# Docker Compose Runbook

## Launching the stack
```bash
docker compose up --build
```

## Verifying the stack

### Health check
```bash
curl http://localhost:8000/health
```

### Rate-limit headers
```bash
curl -i http://localhost:8000/plans
```

### Frontend
Open `http://localhost:8501`

### Worker logs
```bash
docker compose logs -f worker
```

## Capturing the EX3 trace excerpt
```bash
uv run python scripts/capture_trace_excerpt.py
```
