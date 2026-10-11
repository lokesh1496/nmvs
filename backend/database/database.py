import os
from contextlib import contextmanager
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "lokesh@1496")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "nmvs")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
)

print(f"Database configured for PostgreSQL: '{POSTGRES_USER}' at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager yielding a database session with automatic commit/rollback.
    Useful in scripts and background tasks.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db(bind_engine=None) -> None:
    """Initialize all database tables in PostgreSQL."""
    target_engine = bind_engine or engine
    Base.metadata.create_all(bind=target_engine)


def get_db_stats(session: Optional[Session] = None) -> Dict[str, Any]:
    """Return connection information and record counts for all core tables."""
    from app.users.model import User
    from app.devices.model import Device
    from app.alerts.model import Alert
    from app.monitoring.model import MonitoringHistory
    from app.speed_monitoring.model import DeviceBandwidthHistory

    db = session or SessionLocal()
    try:
        stats = {
            "engine_url": str(engine.url),
            "dialect": engine.dialect.name,
            "tables": {}
        }
        for model in [User, Device, Alert, MonitoringHistory, DeviceBandwidthHistory]:
            tbl_name = model.__tablename__
            try:
                stats["tables"][tbl_name] = db.query(model).count()
            except Exception as e:
                stats["tables"][tbl_name] = f"error: {e}"
        return stats
    finally:
        if session is None:
            db.close()