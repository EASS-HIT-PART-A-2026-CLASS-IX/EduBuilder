from datetime import datetime, timezone
from typing import List, Optional
import uuid

from pydantic import BaseModel, EmailStr, Field as PydanticField
from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=utc_now)


class Course(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", index=True)
    title: str
    content: str
    is_public: bool = Field(default=False)
    weekly_digest: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class CourseCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=120)
    content: str = PydanticField(min_length=1)
    is_public: bool = False


class CourseRead(BaseModel):
    id: str
    owner_id: str
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    title: str
    content: str
    is_public: bool
    weekly_digest: Optional[str] = None
    created_at: datetime


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str = PydanticField(min_length=8)


class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = PydanticField(min_length=8)
    full_name: str = PydanticField(min_length=2, max_length=100)


class ChatRequest(BaseModel):
    prompt: str = PydanticField(min_length=1)
    context: Optional[str] = None


class CoursePage(BaseModel):
    title: str = PydanticField(description="Title of the page")
    content: str = PydanticField(description="Educational content in Markdown format")


class QuizQuestion(BaseModel):
    question: str = PydanticField(description="The multiple choice question")
    options: List[str] = PydanticField(description="List of 4 possible answers")
    correct_answer: str = PydanticField(description="The exact string of the correct option")
    explanation: str = PydanticField(description="Explanation of why this answer is correct")


class CourseGenerationResponse(BaseModel):
    pages: List[CoursePage] = PydanticField(
        description="Exactly 5 pages of structured educational content in Markdown."
    )
    quiz: List[QuizQuestion] = PydanticField(
        description="Exactly 5 multiple-choice questions testing the generated content."
    )
    chat_message: str = PydanticField(
        description="A short follow-up message suggesting the next topic and asking whether to continue or save."
    )


class DraftState(BaseModel):
    messages: list
    course_pages: list
    current_page_index: int
    last_saved_course_id: Optional[str] = None
    course_is_public: bool = False
