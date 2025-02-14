from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from labelu.internal.common.config import settings

engine = None
database_url = settings.DATABASE_URL

if settings.DATABASE_URL.startswith('mysql'):
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
else:
    # connect_args is needed only for SQLite. It's not needed for other databases
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=True,
    )

SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)

Base = declarative_base()

# create database tables
def init_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
