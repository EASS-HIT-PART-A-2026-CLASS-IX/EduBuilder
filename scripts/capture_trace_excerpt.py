from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests
from redis import Redis

DEFAULT_API_URL = os.environ.get("TRACE_API_URL", "http://localhost:8000")
DEFAULT_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def build_trace_excerpt(base_url: str, redis_url: str) -> str:
    checks = [
        ("GET /health", f"{base_url}/health"),
        ("GET /plans", f"{base_url}/plans"),
        ("GET /plans/shared", f"{base_url}/plans/shared"),
    ]

    lines: list[str] = ["```text", "# local-redis-trace"]
    for label, url in checks:
        response = requests.get(url, timeout=5)
        lines.append(f"{label} -> {response.status_code}")

    redis_client = Redis.from_url(redis_url, decode_responses=True)
    trace_key = "trace:edubuilder:demo"
    try:
        lines.append(f"REDIS PING -> {redis_client.ping()}")
        redis_client.setex(trace_key, 60, "worker-idempotency-ok")
        lines.append(f"REDIS SETEX {trace_key} -> OK")
        lines.append(f"REDIS GET {trace_key} -> {redis_client.get(trace_key)}")
    finally:
        redis_client.close()

    lines.append("```")
    return "\n".join(lines)


def inject_excerpt(notes_path: Path, excerpt: str) -> None:
    content = notes_path.read_text(encoding="utf-8")
    start_marker = "<!-- TRACE_EXCERPT_START -->"
    end_marker = "<!-- TRACE_EXCERPT_END -->"

    if start_marker not in content or end_marker not in content:
        raise RuntimeError("Trace markers were not found in docs/EX3-notes.md")

    before, remainder = content.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)
    updated = before + start_marker + "\n" + excerpt + "\n" + end_marker + after
    notes_path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a local Redis-backed trace excerpt into docs/EX3-notes.md.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--redis-url", default=DEFAULT_REDIS_URL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    notes_path = project_root / "docs" / "EX3-notes.md"
    excerpt = build_trace_excerpt(args.api_url, args.redis_url)
    inject_excerpt(notes_path, excerpt)
    print("Injected a local Redis-backed trace excerpt into docs/EX3-notes.md")


if __name__ == "__main__":
    main()
