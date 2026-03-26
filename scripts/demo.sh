#!/usr/bin/env bash
set -euo pipefail

API_URL="${TRACE_API_URL:-http://localhost:8000}"
TRACE_USER_EMAIL="${TRACE_USER_EMAIL:-trace-demo@example.com}"
TRACE_USER_PASSWORD="${TRACE_USER_PASSWORD:-tracepass123}"
TRACE_USER_NAME="${TRACE_USER_NAME:-Trace Demo}"

export TRACE_API_URL="$API_URL"
export TRACE_USER_EMAIL
export TRACE_USER_PASSWORD
export TRACE_USER_NAME

echo "=== EduBuilder EX3 Demo ==="
echo "1. Stopping any previous local stack..."
docker compose down -v >/dev/null 2>&1 || true

echo "2. Building and starting the stack..."
docker compose up -d --build

echo "3. Waiting for the API health endpoint..."
for i in {1..30}; do
  if curl -fsS "$API_URL/health" >/dev/null 2>&1; then
    echo "   API is healthy."
    break
  fi
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "API did not become healthy in time."
    exit 1
  fi
done

echo "4. Creating a public demo course through the authenticated API..."
uv run python - <<'PY'
import os
import time

import requests

api_url = os.environ["TRACE_API_URL"]
email = os.environ["TRACE_USER_EMAIL"]
password = os.environ["TRACE_USER_PASSWORD"]
full_name = os.environ["TRACE_USER_NAME"]

register = requests.post(
    f"{api_url}/auth/register",
    json={"email": email, "password": password, "full_name": full_name},
    timeout=20,
)
if register.status_code == 200:
    token = register.json()["access_token"]
else:
    login = requests.post(
        f"{api_url}/auth/login",
        json={"email": email, "password": password},
        timeout=20,
    )
    login.raise_for_status()
    token = login.json()["access_token"]

create = requests.post(
    f"{api_url}/courses",
    json={
        "title": f"Weekly Digest Demo {int(time.time())}",
        "content": "A short public course used to exercise the weekly digest enhancement.",
        "is_public": True,
    },
    headers={"Authorization": f"Bearer {token}"},
    timeout=20,
)
create.raise_for_status()
course = create.json()
print(f"Created course: {course['title']}")
PY

echo "5. Triggering the worker so the weekly digest enhancement runs..."
docker compose run --rm worker python scripts/refresh.py

echo "6. Refreshing the Redis trace excerpt required in docs/EX3-notes.md..."
uv run python scripts/capture_trace_excerpt.py

echo "7. Quick checks:"
curl "$API_URL/health"
echo
curl -I "$API_URL/courses" || true
echo

echo "8. Open these URLs:"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo

echo "9. What this demo already exercised:"
echo "   - authenticated course creation"
echo "   - public course listing"
echo "   - weekly digest worker run"
echo "   - Redis-backed trace capture into docs/EX3-notes.md"
echo

echo "10. Showing recent worker logs. Press Ctrl+C to stop."
docker compose logs --tail=50 -f worker
