from collections.abc import Generator

from app.database.session import SessionLocal


def get_db() -> Generator:
    """Provide one SQLAlchemy session per HTTP request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()