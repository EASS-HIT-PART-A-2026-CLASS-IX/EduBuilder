# EX2 Notes – EduBuilder Frontend

This file presents **EX2 separately** from the richer EX3 interface.

## Goal
Show a lightweight Streamlit interface connected to the EX1 API as-is.

## Files used for EX2
- `frontend/app_ex2.py`
- `poseai_backend/main_ex1.py`
- `docs/EX2-notes.md`

## Recommended EX2 run
Run the API first, then launch the EX2 interface:

```bash
uv run uvicorn poseai_backend.main_ex1:app --reload
uv run streamlit run frontend/app_ex2.py
```

## What this version includes
- lists existing plans immediately from the backend
- allows adding a new plan in one screen
- no authentication or security prompts
- one small extra:
  - summary metrics for the current catalog
  - CSV export of the current catalog

## Expected quick flow
1. Start the FastAPI backend.
2. Start the Streamlit frontend.
3. Open the page and view the current catalog.
4. Add a new plan from the form.
5. Optionally export the catalog to CSV.
