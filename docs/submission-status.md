# Submission Status Check

This file records what can and cannot be verified from the repository itself.

## Verified from the repository snapshot
- Alembic migrations now exist in `alembic/`.
- GitHub Actions CI now exists in `.github/workflows/ci.yml`.
- Compose and runbook documentation now include migration, pytest, and Schemathesis instructions.

## Not verifiable from code alone
### AWS Academy prerequisite
Cannot be verified from this repository. This must be confirmed from your AWS Academy account or course platform.

### `uv run pytest` succeeded locally
Not proven by the repository snapshot alone. You must run:

```bash
uv sync
uv run python -m scripts.migrate
uv run pytest
```

and keep the terminal output or screenshot if you want evidence.

### Bonus screen capture
No `.mp4`, `.mov`, or `.webm` bonus screen capture file was found in the repository snapshot that was checked.

### GitHub Classroom repository / tags
The checked repository snapshot had:

```text
origin: https://github.com/rotempasharel1/EduBuilder.git
```

No Git tags were present in the checked snapshot.

If your instructor requires tags, create one for the final submission, for example:

```bash
git tag ex3-final
git push origin ex3-final
```

If your instructor requires GitHub Classroom specifically, confirm that the submission repository URL matches the classroom repository you were assigned.
