from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests

DEFAULT_API_URL = os.environ.get("TRACE_API_URL", "http://localhost:8000")


def build_trace_excerpt(base_url: str) -> str:
    checks = [
        ("GET /health", f"{base_url}/health"),
        ("GET /plans", f"{base_url}/plans"),
        ("GET /plans/shared", f"{base_url}/plans/shared"),
    ]

    lines: list[str] = ["```text", "# local-http-trace"]
    for label, url in checks:
        response = requests.get(url, timeout=5)
        lines.append(f"{label} -> {response.status_code}")
    lines.append("```")
    return "\n".join(lines)


def inject_excerpt(notes_path: Path, excerpt: str) -> None:
    placeholder = "[PASTE LOCAL TRACE EXCERPT HERE]"
    content = notes_path.read_text(encoding="utf-8")

    if placeholder not in content:
        raise RuntimeError("Placeholder was not found in docs/EX3-notes.md")

    updated = content.replace(placeholder, excerpt)
    notes_path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a local HTTP trace excerpt into docs/EX3-notes.md.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    notes_path = project_root / "docs" / "EX3-notes.md"
    excerpt = build_trace_excerpt(args.api_url)
    inject_excerpt(notes_path, excerpt)
    print("Injected a local HTTP trace excerpt into docs/EX3-notes.md")


if __name__ == "__main__":
    main()
