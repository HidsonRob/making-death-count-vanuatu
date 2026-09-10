from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "mortality.db"
DATABASE_URL = URL.create("sqlite", database=str(DB_PATH))

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    from models import (  # noqa: F401
        Cause,
        CauseDetail,
        Dataset,
        MonthlyDeath,
        Place,
        SexCause,
        SexTotal,
    )

    Base.metadata.create_all(bind=engine)
