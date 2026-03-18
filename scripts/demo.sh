#!/usr/bin/env bash
set -euo pipefail

echo "=== EduBuilder Local Demo ==="
echo "1. Stopping any previous local stack..."
docker compose down -v >/dev/null 2>&1 || true

echo "2. Building and starting the stack..."
docker compose up -d --build

echo "3. Waiting for the API health endpoint..."
for i in {1..30}; do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    echo "   API is healthy."
    break
  fi
  sleep 2
  if [ "$i" -eq 30 ]; then
    echo "API did not become healthy in time."
    exit 1
  fi
done

echo "4. Seeding demo data inside the API container..."
docker compose exec -T api python scripts/seed.py || true

echo "5. Health check:"
curl http://localhost:8000/health
echo

echo "6. Rate-limit headers check:"
curl -I http://localhost:8000/courses || true
echo

echo "7. Open these URLs:"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo

echo "8. Suggested seeded users:"
echo "   admin@example.com / adminpass123"
echo "   user@example.com / userpass123"
echo

echo "9. Showing live logs. Press Ctrl+C to stop log tailing; containers will keep running."
docker compose logs -f
