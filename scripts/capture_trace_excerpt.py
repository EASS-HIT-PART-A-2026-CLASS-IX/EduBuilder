from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import requests

START_MARKER = "<!-- TRACE_EXCERPT_START -->"
END_MARKER = "<!-- TRACE_EXCERPT_END -->"
DEFAULT_API_URL = os.environ.get("TRACE_API_URL", "http://localhost:8000")
TRACE_USER_EMAIL = os.environ.get("TRACE_USER_EMAIL", "trace-demo@example.com")
TRACE_USER_PASSWORD = os.environ.get("TRACE_USER_PASSWORD", "tracepass123")
TRACE_USER_NAME = os.environ.get("TRACE_USER_NAME", "Trace Demo")

COMMON_DOCKER_FAILURE_SNIPPETS = (
    "failed to connect to the docker api",
    "dockerdesktoplinuxengine",
    "cannot connect to the docker daemon",
    "is the docker daemon running",
    "error during connect",
)


def run_command(command: list[str], timeout: int = 60, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=check,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ensure_docker_compose_available() -> None:
    try:
        result = run_command(["docker", "compose", "version"], timeout=20, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Docker is not installed or not available on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"Docker Compose is unavailable: {details}") from exc

    text = (result.stdout + "\n" + result.stderr).strip().lower()
    for snippet in COMMON_DOCKER_FAILURE_SNIPPETS:
        if snippet in text:
            raise RuntimeError(
                "Docker Compose is installed but the Docker daemon is not reachable. "
                "Start Docker Desktop or the Docker daemon and retry."
            )


def wait_for_api(base_url: str, timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None

    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            response.raise_for_status()
            return
        except Exception as exc:  # pragma: no cover - local environment helper
            last_error = exc
            time.sleep(2)

    raise RuntimeError(f"API did not become ready at {base_url!r}. Last error: {last_error}")


def start_redis_monitor() -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["docker", "compose", "exec", "-T", "redis", "redis-cli", "MONITOR"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def get_or_create_token(base_url: str) -> str:
    register_payload = {
        "email": TRACE_USER_EMAIL,
        "password": TRACE_USER_PASSWORD,
        "full_name": TRACE_USER_NAME,
    }
    register_response = requests.post(
        f"{base_url}/auth/register",
        json=register_payload,
        timeout=15,
    )
    if register_response.status_code == 200:
        return register_response.json()["access_token"]

    login_payload = {
        "email": TRACE_USER_EMAIL,
        "password": TRACE_USER_PASSWORD,
    }
    login_response = requests.post(
        f"{base_url}/auth/login",
        json=login_payload,
        timeout=15,
    )
    login_response.raise_for_status()
    return login_response.json()["access_token"]


def create_demo_course(base_url: str, token: str) -> None:
    payload = {
        "title": f"Trace Demo Course {int(time.time())}",
        "content": "Short content created only to exercise Redis-backed flows.",
        "is_public": True,
    }
    response = requests.post(
        f"{base_url}/courses",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    response.raise_for_status()


def trigger_api_activity(base_url: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    requests.get(f"{base_url}/courses", timeout=10).raise_for_status()
    requests.get(f"{base_url}/courses/shared", timeout=10).raise_for_status()
    requests.get(f"{base_url}/me", headers=headers, timeout=10).raise_for_status()
    requests.get(f"{base_url}/courses/my", headers=headers, timeout=10).raise_for_status()


def trigger_worker_activity() -> str:
    command = ["docker", "compose", "run", "--rm", "worker", "python", "scripts/refresh.py"]
    result = run_command(command, timeout=120, check=True)
    return result.stdout.strip() or "(worker completed without stdout)"


def stop_monitor(process: subprocess.Popen[str]) -> tuple[str, str]:
    if process.poll() is None:
        if os.name == "nt":
            process.send_signal(signal.CTRL_BREAK_EVENT)  # pragma: no cover - windows only
        else:
            process.terminate()

    try:
        stdout, stderr = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:  # pragma: no cover - local environment helper
        process.kill()
        stdout, stderr = process.communicate()

    return stdout, stderr


def tail_lines(text: str, max_lines: int = 40) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "(no lines captured)"
    return "\n".join(lines[-max_lines:])


def contains_common_docker_failure(text: str) -> bool:
    lowered = text.lower()
    return any(snippet in lowered for snippet in COMMON_DOCKER_FAILURE_SNIPPETS)


def validate_capture(monitor_stdout: str, monitor_stderr: str, worker_output: str) -> None:
    if contains_common_docker_failure(monitor_stdout) or contains_common_docker_failure(monitor_stderr):
        raise RuntimeError(
            "Docker reported a daemon connectivity problem while capturing the Redis trace. "
            "Make sure Docker is running and retry."
        )

    if "(no lines captured)" in tail_lines(monitor_stdout, max_lines=50):
        raise RuntimeError(
            "Redis MONITOR did not capture any lines. "
            "Verify that the Compose stack is up and that the API and worker generated Redis activity."
        )

    if contains_common_docker_failure(worker_output):
        raise RuntimeError(
            "The worker trigger failed because Docker was not reachable. "
            "Start Docker and rerun the capture."
        )


def build_redis_trace_excerpt(base_url: str) -> str:
    ensure_docker_compose_available()
    wait_for_api(base_url)
    token = get_or_create_token(base_url)
    monitor_process = start_redis_monitor()

    try:
        time.sleep(2)
        create_demo_course(base_url, token)
        trigger_api_activity(base_url, token)
        worker_output = trigger_worker_activity()
        time.sleep(2)
    finally:
        monitor_stdout, monitor_stderr = stop_monitor(monitor_process)

    validate_capture(monitor_stdout, monitor_stderr, worker_output)

    monitor_block = tail_lines(monitor_stdout, max_lines=50)
    worker_block = tail_lines(worker_output, max_lines=20)
    stderr_block = tail_lines(monitor_stderr, max_lines=20) if monitor_stderr.strip() else "(empty)"

    return (
        "```text\n"
        "# redis-monitor\n"
        f"{monitor_block}\n\n"
        "# worker-trigger\n"
        f"{worker_block}\n\n"
        "# redis-monitor-stderr\n"
        f"{stderr_block}\n"
        "```"
    )


def inject_excerpt(notes_path: Path, excerpt_block: str) -> None:
    content = notes_path.read_text(encoding="utf-8")
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1:
        raise RuntimeError("Trace markers were not found in docs/EX3-notes.md")

    start += len(START_MARKER)
    new_content = content[:start] + "\n\n" + excerpt_block + "\n\n" + content[end:]
    notes_path.write_text(new_content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a real Redis monitor excerpt into docs/EX3-notes.md.")
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help="Base URL for the local API. Defaults to TRACE_API_URL or http://localhost:8000.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    notes_path = project_root / "docs" / "EX3-notes.md"

    try:
        excerpt = build_redis_trace_excerpt(args.api_url)
        inject_excerpt(notes_path, excerpt)
    except Exception as exc:
        raise SystemExit(
            "Trace capture failed and docs/EX3-notes.md was left unchanged.\n"
            f"Reason: {exc}"
        ) from exc

    print("Injected a real local Redis trace excerpt into docs/EX3-notes.md")


if __name__ == "__main__":
    main()
