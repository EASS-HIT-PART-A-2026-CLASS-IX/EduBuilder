from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone
from itertools import count
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="EduBuilder EX1/EX2 API", version="1.1.0")

# -----------------------------
# In-memory stores
# -----------------------------

USERS: Dict[str, "User"] = {}
USER_EMAIL_INDEX: Dict[str, str] = {}
TOKENS: Dict[str, str] = {}
PLANS: Dict[str, "Plan"] = {}
DRAFTS: Dict[str, dict[str, Any]] = {}

_USER_IDS = count(1)
_PLAN_IDS = count(1)

security = HTTPBearer(auto_error=False)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com").strip().lower()


# -----------------------------
# Models
# -----------------------------

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    password: str
    role: str = "user"
    created_at: str


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
    owner_id: str
    title: str
    goal: str
    cues: str
    level: str
    is_public: bool = True
    weekly_digest: Optional[str] = None
    created_at: str


class CoursePayload(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    is_public: bool = False


class ChatGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    context: str = ""


class ChatDraftPayload(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)
    course_pages: list[dict[str, Any]] = Field(default_factory=list)
    current_page_index: int = 0
    last_saved_course_id: Optional[str] = None
    course_is_public: bool = False


# -----------------------------
# Helpers
# -----------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_user_id() -> str:
    return f"u{next(_USER_IDS)}"


def _new_plan_id() -> str:
    return f"p{next(_PLAN_IDS)}"


def _issue_token(user_id: str) -> str:
    token = secrets.token_urlsafe(24)
    TOKENS[token] = user_id
    return token


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    token = credentials.credentials
    user_id = TOKENS.get(token)
    if not user_id or user_id not in USERS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return USERS[user_id]


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User | None:
    if credentials is None:
        return None
    user_id = TOKENS.get(credentials.credentials)
    if not user_id:
        return None
    return USERS.get(user_id)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _owner_for_plan(plan: Plan) -> User | None:
    return USERS.get(plan.owner_id)


def _plan_to_course(plan: Plan) -> dict[str, Any]:
    owner = _owner_for_plan(plan)
    return {
        "id": plan.id,
        "owner_id": plan.owner_id,
        "owner_name": owner.full_name if owner else "Unknown",
        "owner_email": owner.email if owner else "Unknown",
        "title": plan.title,
        "content": plan.goal,
        "is_public": plan.is_public,
        "weekly_digest": plan.weekly_digest,
        "created_at": plan.created_at,
    }


def _plan_to_api(plan: Plan) -> dict[str, Any]:
    owner = _owner_for_plan(plan)
    return {
        "id": plan.id,
        "owner_id": plan.owner_id,
        "owner_name": owner.full_name if owner else None,
        "owner_email": owner.email if owner else None,
        "title": plan.title,
        "goal": plan.goal,
        "cues": plan.cues,
        "level": plan.level,
        "is_public": plan.is_public,
        "weekly_digest": plan.weekly_digest,
        "created_at": plan.created_at,
    }


def _infer_topic(prompt: str) -> str:
    text = prompt.strip().rstrip(".")
    if not text:
        return "General Learning"
    lowered = text.lower()
    prefixes = [
        "create a course about ",
        "build a course about ",
        "make a course about ",
        "course about ",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip().title() or "General Learning"
    return text.title()


def _existing_content_page_count(context: str) -> int:
    return sum(1 for line in context.splitlines() if line.strip().startswith("### "))


def _build_page(topic: str, chapter_number: int) -> dict[str, str]:
    if chapter_number == 1:
        return {
            "title": f"{topic}: Foundations",
            "content": (
                f"Welcome to **{topic}**.\n\n"
                "In this first chapter, we introduce the central ideas, explain why the topic matters, "
                "and connect it to practical examples.\n\n"
                "- Define the topic clearly\n"
                "- Understand the main goals\n"
                "- See one simple real-life example"
            ),
        }
    if chapter_number == 2:
        return {
            "title": f"{topic}: Core Concepts",
            "content": (
                f"This chapter develops the main concepts in **{topic}**.\n\n"
                "- Learn the key terms\n"
                "- Compare related ideas\n"
                "- Avoid common beginner mistakes"
            ),
        }
    if chapter_number == 3:
        return {
            "title": f"{topic}: Applications and Practice",
            "content": (
                f"Now we move from theory to practice in **{topic}**.\n\n"
                "- Apply the concepts in a small task\n"
                "- Explain your reasoning\n"
                "- Reflect on what you learned"
            ),
        }
    return {
        "title": f"{topic}: Chapter {chapter_number}",
        "content": (
            f"This chapter extends **{topic}** with one more focused angle.\n\n"
            "- Brief recap\n"
            "- One deeper example\n"
            "- One reflection question"
        ),
    }


def _build_quiz(topic: str, chapter_number: int) -> list[dict[str, Any]]:
    return [
        {
            "question": f"What is the main goal of learning {topic} in this chapter?",
            "options": [
                "To memorize random facts",
                "To understand the core ideas and apply them",
                "To skip all examples",
                "To focus only on advanced research",
            ],
            "correct_answer": "To understand the core ideas and apply them",
            "explanation": "A good starter chapter builds understanding and practical use.",
        },
        {
            "question": f"What helps most when studying {topic}?",
            "options": [
                "Connecting concepts to examples",
                "Ignoring definitions",
                "Skipping review",
                "Reading only titles",
            ],
            "correct_answer": "Connecting concepts to examples",
            "explanation": "Examples make the core concepts easier to understand and remember.",
        },
        {
            "question": f"After chapter {chapter_number}, what should the learner be able to do?",
            "options": [
                "Explain the main ideas clearly",
                "Master every advanced topic",
                "Avoid asking questions",
                "Ignore practice tasks",
            ],
            "correct_answer": "Explain the main ideas clearly",
            "explanation": "The goal is to understand and explain the key ideas, not to master every edge case.",
        },
    ]


def _seed_public_course() -> None:
    if not USERS:
        admin = User(
            id=_new_user_id(),
            email=ADMIN_EMAIL,
            full_name="Admin Teacher",
            password="adminpass123",
            role="admin",
            created_at=_now_iso(),
        )
        USERS[admin.id] = admin
        USER_EMAIL_INDEX[admin.email] = admin.id

    if PLANS:
        return

    owner_id = next(iter(USERS.keys()))
    sample = Plan(
        id=_new_plan_id(),
        owner_id=owner_id,
        title="Python Basics Study Plan",
        goal=(
            "### Python Basics\n"
            "Learn variables, loops, and functions with short examples and daily practice.\n\n"
            "### Practice\n"
            "Write three mini examples and explain what each one does."
        ),
        cues="Start small, practice daily, and summarize in your own words.",
        level="Beginner",
        is_public=True,
        weekly_digest="Weekly focus: review variables, loops, and one small function.",
        created_at=_now_iso(),
    )
    PLANS[sample.id] = sample


_seed_public_course()


# -----------------------------
# Health + EX1 CRUD
# -----------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.1.0"}


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
    owner_id = next(iter(USERS.keys()))
    plan = Plan(
        id=_new_plan_id(),
        owner_id=owner_id,
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


# -----------------------------
# Auth for frontend/app_ex2.py
# -----------------------------

@app.post("/auth/register")
def register(user_data: EmailRegisterRequest) -> dict[str, str]:
    email = _normalize_email(str(user_data.email))
    if email in USER_EMAIL_INDEX:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=_new_user_id(),
        email=email,
        full_name=user_data.full_name.strip(),
        password=user_data.password,
        role="admin" if email == ADMIN_EMAIL else "user",
        created_at=_now_iso(),
    )
    USERS[user.id] = user
    USER_EMAIL_INDEX[email] = user.id

    token = _issue_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/login")
def login(user_data: EmailLoginRequest) -> dict[str, str]:
    email = _normalize_email(str(user_data.email))
    user_id = USER_EMAIL_INDEX.get(email)
    if not user_id:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    user = USERS[user_id]
    if user.password != user_data.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = _issue_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def me(user: User = Depends(get_current_user)) -> dict[str, str]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }


# -----------------------------
# Chat helpers for frontend/app_ex2.py
# -----------------------------

@app.post("/chat/generate_course")
def generate_course(
    payload: ChatGenerateRequest,
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    topic = _infer_topic(payload.prompt)
    current_pages = _existing_content_page_count(payload.context)
    lowered = payload.prompt.lower()

    wants_continue = any(
        phrase in lowered
        for phrase in ["continue", "next chapter", "another chapter", "add chapter", "keep building"]
    )

    if wants_continue and current_pages > 0:
        next_page = _build_page(topic, current_pages + 1)
        pages = [next_page]
        quiz = _build_quiz(topic, current_pages + 1) if (current_pages + 1) % 2 == 0 else []
        chat_message = f"I added the next chapter for **{topic}**."
    else:
        pages = [_build_page(topic, 1), _build_page(topic, 2), _build_page(topic, 3)]
        quiz = _build_quiz(topic, 3)
        chat_message = f"I created a starter course for **{topic}** with three lesson pages and a short quiz."

    return {"chat_message": chat_message, "pages": pages, "quiz": quiz}


@app.get("/chat/draft")
def get_chat_draft(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return DRAFTS.get(user.id, {})


@app.post("/chat/draft")
def save_chat_draft(
    payload: ChatDraftPayload,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    DRAFTS[user.id] = payload.model_dump()
    return {"status": "saved"}


@app.delete("/chat/draft")
def delete_chat_draft(user: User = Depends(get_current_user)) -> dict[str, str]:
    DRAFTS.pop(user.id, None)
    return {"status": "deleted"}


# -----------------------------
# Course endpoints expected by frontend/app_ex2.py
# -----------------------------

@app.get("/courses/shared")
def get_shared_courses() -> list[dict[str, Any]]:
    public_plans = [plan for plan in PLANS.values() if plan.is_public]
    public_plans.sort(key=lambda item: item.created_at, reverse=True)
    return [_plan_to_course(plan) for plan in public_plans]


@app.get("/courses/my")
def get_my_courses(user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    mine = [plan for plan in PLANS.values() if plan.owner_id == user.id]
    mine.sort(key=lambda item: item.created_at, reverse=True)
    return [_plan_to_course(plan) for plan in mine]


@app.post("/courses")
def create_course(
    payload: CoursePayload,
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    plan = Plan(
        id=_new_plan_id(),
        owner_id=user.id,
        title=payload.title,
        goal=payload.content,
        cues="EduBuilder generated course content",
        level="General",
        is_public=payload.is_public,
        created_at=_now_iso(),
    )
    PLANS[plan.id] = plan
    return _plan_to_course(plan)


@app.put("/courses/{course_id}")
def update_course(
    course_id: str,
    payload: CoursePayload,
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    existing = PLANS.get(course_id)
    if existing is None or existing.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Course not found or no permission")

    updated = existing.model_copy(
        update={
            "title": payload.title,
            "goal": payload.content,
            "is_public": payload.is_public,
        }
    )
    PLANS[course_id] = updated
    return _plan_to_course(updated)


@app.delete("/courses/{course_id}")
def delete_course(
    course_id: str,
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    existing = PLANS.get(course_id)
    if existing is None or existing.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Course not found or no permission")
    del PLANS[course_id]
    return {"status": "success"}


@app.get("/admin/courses")
def get_all_courses(admin: User = Depends(require_admin)) -> list[dict[str, Any]]:
    plans = list(PLANS.values())
    plans.sort(key=lambda item: item.created_at, reverse=True)
    return [_plan_to_course(plan) for plan in plans]


@app.delete("/admin/courses/{course_id}")
def delete_course_as_admin(
    course_id: str,
    admin: User = Depends(require_admin),
) -> dict[str, str]:
    if course_id in PLANS:
        del PLANS[course_id]
    return {"status": "success"}
