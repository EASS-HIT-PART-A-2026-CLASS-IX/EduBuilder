from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="EduBuilder EX1 API", version="1.0.0")


class PlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1, max_length=240)
    cues: str = Field(min_length=1)
    level: str = Field(min_length=1, max_length=40)
    is_public: bool = True


class PlanUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1, max_length=240)
    cues: str = Field(min_length=1)
    level: str = Field(min_length=1, max_length=40)
    is_public: bool = True


class Plan(BaseModel):
    id: str
    title: str
    goal: str
    cues: str
    level: str
    is_public: bool = True
    created_at: str


PLANS: dict[str, Plan] = {}
_PLAN_IDS = count(1)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_plan_id() -> str:
    return f"p{next(_PLAN_IDS)}"


def _plan_to_api(plan: Plan) -> dict[str, Any]:
    return {
        "id": plan.id,
        "title": plan.title,
        "goal": plan.goal,
        "cues": plan.cues,
        "level": plan.level,
        "is_public": plan.is_public,
        "created_at": plan.created_at,
    }


def _seed_demo_plan() -> None:
    if PLANS:
        return

    demo = Plan(
        id=_new_plan_id(),
        title="Python Basics Study Plan",
        goal="Learn variables, loops, and functions through short daily practice.",
        cues="Start with one small example, then explain it in your own words.",
        level="Beginner",
        is_public=True,
        created_at=_now_iso(),
    )
    PLANS[demo.id] = demo


_seed_demo_plan()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/plans")
def list_plans() -> list[dict[str, Any]]:
    return [_plan_to_api(plan) for plan in PLANS.values()]


@app.get("/plans/{plan_id}")
def get_plan(plan_id: str) -> dict[str, Any]:
    plan = PLANS.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _plan_to_api(plan)


@app.post("/plans")
def create_plan(payload: PlanCreate) -> dict[str, Any]:
    plan = Plan(
        id=_new_plan_id(),
        title=payload.title,
        goal=payload.goal,
        cues=payload.cues,
        level=payload.level,
        is_public=payload.is_public,
        created_at=_now_iso(),
    )
    PLANS[plan.id] = plan
    return _plan_to_api(plan)


@app.put("/plans/{plan_id}")
def update_plan(plan_id: str, payload: PlanUpdate) -> dict[str, Any]:
    existing = PLANS.get(plan_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    updated = existing.model_copy(
        update={
            "title": payload.title,
            "goal": payload.goal,
            "cues": payload.cues,
            "level": payload.level,
            "is_public": payload.is_public,
        }
    )
    PLANS[plan_id] = updated
    return _plan_to_api(updated)


@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: str) -> dict[str, str]:
    if plan_id not in PLANS:
        raise HTTPException(status_code=404, detail="Plan not found")
    del PLANS[plan_id]
    return {"status": "success"}
