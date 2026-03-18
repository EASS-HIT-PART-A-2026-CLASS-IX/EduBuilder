from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config


def get_alembic_config() -> Config:
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    if "DATABASE_URL" in os.environ:
        config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    return config


def run_migrations() -> None:
    command.upgrade(get_alembic_config(), "head")


if __name__ == "__main__":
    run_migrations()
