from sqlmodel import Session, select

from poseai_backend.auth import get_password_hash
from poseai_backend.database import engine
from poseai_backend.models import Plan, User


def seed() -> None:
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("adminpass123"),
                full_name="Admin Teacher",
                role="admin",
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)

        existing = session.exec(select(Plan)).first()
        if existing:
            return

        plans = [
            Plan(
                owner_id=admin.id,
                title="Python basics study plan",
                goal="Review variables, loops, and functions",
                cues="Start with short examples, practice every day, and summarize each topic in your own words.",
                level="Beginner",
                is_public=True,
            ),
            Plan(
                owner_id=admin.id,
                title="Databases revision plan",
                goal="Strengthen SQL and schema design",
                cues="Practice SELECT, JOIN, and filtering queries, then design one small schema from scratch.",
                level="Intermediate",
                is_public=True,
            ),
        ]
        session.add_all(plans)
        session.commit()


if __name__ == "__main__":
    seed()
