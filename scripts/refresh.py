import os
from datetime import timedelta

import anyio
from google import genai
from redis.asyncio import Redis
from sqlmodel import Session, create_engine, select

from backend.models import Course

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MAX_CONCURRENCY = int(os.environ.get("WORKER_MAX_CONCURRENCY", "3"))
MAX_RETRIES = int(os.environ.get("WORKER_MAX_RETRIES", "3"))
RETRY_DELAY_SECONDS = float(os.environ.get("WORKER_RETRY_DELAY_SECONDS", "2"))
DIGEST_TTL = timedelta(days=7)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
redis = Redis.from_url(REDIS_URL, decode_responses=True)
genai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def fetch_public_courses() -> list[Course]:
    with Session(engine) as session:
        statement = select(Course).where(
            Course.is_public == True,  # noqa: E712 - SQLModel expression
            Course.title != "__DRAFT_STATE__",
        )
        return list(session.exec(statement).all())


def save_digest_to_db(course_id: str, digest: str) -> None:
    with Session(engine) as session:
        course = session.get(Course, course_id)
        if course is None:
            return
        course.weekly_digest = digest
        session.add(course)
        session.commit()


async def generate_digest_for_course(course_id: str, title: str, content: str) -> str | None:
    if not genai_client:
        print(f"[Worker] Skipping Gemini call for {title} (no API key configured).")
        return f"Digest for {title} (mocked)"

    prompt = (
        "Write a 2-sentence weekly digest or recommendation summarizing the following "
        "course content to entice new learners. "
        f"Title: {title}\n"
        f"Content: {content[:1000]}"
    )

    try:
        response = await anyio.to_thread.run_sync(
            lambda: genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        )
    except Exception as exc:
        print(f"[Worker] Error generating digest for {course_id}: {exc}")
        return None

    text = getattr(response, "text", "") or ""
    text = text.replace("\n", " ").strip()
    return text or None


async def process_course(course_id: str, title: str, content: str, limiter: anyio.CapacityLimiter) -> None:
    async with limiter:
        cache_key = f"course_digest_processed:{course_id}"
        if await redis.get(cache_key):
            print(f"[Worker] Skipping {course_id} ({title}) - already processed recently.")
            return

        print(f"[Worker] Processing {course_id} ({title})...")

        digest: str | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            digest = await generate_digest_for_course(course_id, title, content)
            if digest:
                break

            if attempt < MAX_RETRIES:
                print(f"[Worker] Retrying {course_id} (attempt {attempt}/{MAX_RETRIES})...")
                await anyio.sleep(RETRY_DELAY_SECONDS)

        if not digest:
            print(f"[Worker] FAILED | {title} | Could not generate digest.")
            return

        await anyio.to_thread.run_sync(save_digest_to_db, course_id, digest)
        await redis.setex(cache_key, DIGEST_TTL, "1")
        print(f"[Worker] SUCCESS | {title} | Digest: {digest[:100]}...")


async def main() -> None:
    print("[Worker] Starting background refresh worker...")

    try:
        courses = await anyio.to_thread.run_sync(fetch_public_courses)
        if not courses:
            print("[Worker] No public courses found. Exiting.")
            return

        print(f"[Worker] Found {len(courses)} public courses to process.")
        limiter = anyio.CapacityLimiter(MAX_CONCURRENCY)

        async with anyio.create_task_group() as task_group:
            for course in courses:
                task_group.start_soon(
                    process_course,
                    course.id,
                    course.title,
                    course.content,
                    limiter,
                )
    finally:
        close_method = getattr(redis, "aclose", None) or getattr(redis, "close", None)
        if close_method is not None:
            result = close_method()
            if hasattr(result, "__await__"):
                await result

    print("[Worker] Finished processing all courses.")


if __name__ == "__main__":
    anyio.run(main)