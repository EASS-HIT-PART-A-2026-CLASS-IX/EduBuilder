from sqlmodel import Session, select

from backend.auth import get_password_hash
from backend.database import engine
from backend.models import Course, User
from scripts.migrate import run_migrations



def seed_database() -> None:
    print("Applying migrations...")
    run_migrations()

    with Session(engine) as session:
        existing_admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if existing_admin:
            print("Database already seeded. Skipping.")
            return

        print("Seeding initial users...")
        admin_user = User(
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("adminpass123"),
            role="admin",
        )

        standard_user = User(
            email="user@example.com",
            full_name="Jane Doe",
            hashed_password=get_password_hash("userpass123"),
            role="user",
        )

        session.add(admin_user)
        session.add(standard_user)
        session.commit()
        session.refresh(admin_user)
        session.refresh(standard_user)

        print("Seeding sample courses...")
        course1 = Course(
            owner_id=admin_user.id,
            title="Introduction to Python Programming",
            content="""# Chapter 1: Hello World
Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991.

### Example:
```python
print(\"Hello, World!\")
```

### Exercises:
1. Write a script that prints your name.
""",
            is_public=True,
        )

        course2 = Course(
            owner_id=standard_user.id,
            title="Mastering the Art of Italian Cooking",
            content="""# Chapter 1: The Perfect Pasta Dough
To make authentic pasta, you only need flour and eggs. Use 100g of Type '00' flour per large egg.

### Recipe:
1. Mound the flour on a clean surface and make a well in the center.
2. Crack the eggs into the well.
3. Beat with a fork, gradually bringing in flour.
4. Knead for 10 minutes until smooth.

### Chef's Tip:
Always let the dough rest, covered, for at least 30 minutes before rolling it out.
""",
            is_public=True,
        )

        session.add(course1)
        session.add(course2)
        session.commit()

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
