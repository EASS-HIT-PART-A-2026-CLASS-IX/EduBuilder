# Submission Status Check

This file records what can and cannot be verified from the repository itself.

## Verified from the repository snapshot

- The project keeps one consistent domain across EX1–EX3: courses / course catalog / course builder.
- A focused EX1 backend exists in `backend/main_ex1.py`.
- A focused EX2 frontend exists in `frontend/app_ex2.py`.
- EX1 pytest coverage exists in `tests/test_ex1_api.py`.
- EX1 notes exist in `docs/EX1-notes.md`.
- EX2 notes exist in `docs/EX2-notes.md`.
- EX3 notes exist in `docs/EX3-notes.md`.
- Compose orchestration exists in `compose.yaml`.
- Compose runbook documentation exists in `docs/runbooks/compose.md`.
- Async worker logic exists in `scripts/refresh.py`.
- Worker tests exist in `tests/test_worker.py`.
- API tests exist in `tests/test_api.py`.
- OpenAPI contract tests exist in `tests/test_openapi.py`.
- GitHub Actions CI exists in `.github/workflows/ci.yml`.
- `.gitignore` excludes `.env`, virtual environments, and SQLite artifacts.

## Items that appear aligned with the assignment

### EX1
- Dedicated backend service
- CRUD for the core resource
- in-memory storage
- pytest + TestClient coverage
- dedicated notes explaining how to run and test EX1

### EX2
- Lightweight Streamlit interface
- list + add flow available in one screen
- no login prompts in the dedicated EX2 UI
- one small extra: visible count and CSV export
- dedicated notes explaining how to run API and UI side-by-side

### EX3
- FastAPI backend
- SQLite/SQLModel persistence
- Streamlit interface
- Redis service
- async worker
- Compose orchestration
- runbook docs
- JWT auth and role checks
- tests for expired token / missing scope
- enhancement with bounded scope
- local demo script
- CI coverage for migrations + pytest + contract tests

## Not verifiable from code alone

### AWS Academy prerequisite
Cannot be verified from the repository. Confirm from the course platform.

### GitHub Classroom repository
The checked repository URL is:

```text
https://github.com/rotempasharel1/EduBuilder
```

If your instructor requires a specific GitHub Classroom repository, confirm that this is the assigned submission URL.

### Required tags
Tags are not guaranteed by code inspection alone. If your instructor requires tags such as `ex1-final`, `ex2-final`, or `ex3-final`, create and push them manually.

## Recommended final actions before submission

1. Replace the repository README with the updated grader-friendly version.
2. Confirm the final branch is pushed to the correct repository.
3. Confirm whether Git tags are required.
4. Run the relevant local commands one last time:

```bash
uv run pytest
uv run pytest tests/test_ex1_api.py
```

5. If submitting EX3, refresh the log excerpt after a local Compose run:

```bash
python scripts/capture_trace_excerpt.py
```
