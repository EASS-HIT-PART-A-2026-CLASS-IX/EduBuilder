# EX2 Notes – EduBuilder Frontend

This file is for presenting **EX2 separately** from the richer EX3 interface.

## Goal
Show a lightweight Streamlit interface connected to the EduBuilder API.

## File to run
Run the API first, then launch the EX2 interface:

```bash
uv run uvicorn backend.main:app --reload
uv run streamlit run frontend/app_ex2.py
```

If you prefer the fully minimal backend from EX1, you can also use:

```bash
uv run uvicorn backend.main_ex1:app --reload
uv run streamlit run frontend/app_ex2.py
```

## What this version includes
- Lists existing courses immediately
- Allows adding a new course in one screen
- No login or security prompts in the UI
- One small extra:
  - visible course count
  - CSV export of the current catalog

## Expected local URLs
- API: `http://127.0.0.1:8000`
- Streamlit: `http://127.0.0.1:8501`

## Why this file exists
The main EX3 frontend is richer and includes sign-in, private courses, admin features, and AI-assisted flows.

For the EX2 presentation, this file keeps the interface focused and very fast to demonstrate.
