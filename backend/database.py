import os
from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def init_db() -> None:
    """
    EX3 relies on Alembic migrations instead of create_all().

    For quick EX1-style local experiments you may opt in to auto table creation by setting:
        AUTO_CREATE_TABLES=1
    """
    if os.environ.get("AUTO_CREATE_TABLES", "0") == "1":
        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
