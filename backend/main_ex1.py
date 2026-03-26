from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="EduBuilder EX1 API")


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    is_public: bool = True


class CourseRead(CourseCreate):
    id: str
    created_at: str


COURSES: Dict[str, CourseRead] = {}


@app.get("/health")
def health():
    return {"status": "ok", "exercise": "EX1"}


@app.get("/courses")
def list_courses():
    return list(COURSES.values())


@app.get("/courses/{course_id}")
def get_course(course_id: str):
    course = COURSES.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.post("/courses", response_model=CourseRead)
def create_course(payload: CourseCreate):
    course_id = str(uuid4())
    course = CourseRead(
        id=course_id,
        title=payload.title,
        content=payload.content,
        is_public=payload.is_public,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    COURSES[course_id] = course
    return course


@app.put("/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: str, payload: CourseCreate):
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")

    updated = CourseRead(
        id=course_id,
        title=payload.title,
        content=payload.content,
        is_public=payload.is_public,
        created_at=COURSES[course_id].created_at,
    )
    COURSES[course_id] = updated
    return updated


@app.delete("/courses/{course_id}")
def delete_course(course_id: str):
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")

    del COURSES[course_id]
    return {"status": "success"}
