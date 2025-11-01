"""
Database - SQLAlchemy engine and session management

This module provides database connection setup and session management
for the application.

Author: Jonathan Ives (@dollythedog)
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.infra.settings import settings


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_session() -> Session:
    """
    Create a new database session.
    
    This should be used with a context manager or try/finally block
    to ensure the session is properly closed.
    
    Returns:
        Session: SQLAlchemy session
        
    Example:
        >>> session = get_session()
        >>> try:
        ...     result = session.query(PatientContact).first()
        ... finally:
        ...     session.close()
    """
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for database operations.
    
    This context manager automatically commits on success and rolls back on error.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        >>> with session_scope() as session:
        ...     patient = PatientContact(phone_e164="+12145551234")
        ...     session.add(patient)
        ...     # Automatically commits on exit
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_dependency() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Use this as a dependency in FastAPI route handlers.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        >>> from fastapi import Depends
        >>> 
        >>> @app.get("/patients")
        >>> def get_patients(db: Session = Depends(get_db_dependency)):
        ...     return db.query(PatientContact).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """
    Initialize database - create all tables.
    
    WARNING: This should only be used for development/testing.
    In production, use Alembic migrations instead.
    
    Example:
        >>> init_db()
        >>> # All tables now exist in database
    """
    from app.infra.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    
    WARNING: This will delete all data! Use with extreme caution.
    Only for development/testing.
    
    Example:
        >>> drop_db()
        >>> # All tables and data have been deleted
    """
    from app.infra.models import Base
    Base.metadata.drop_all(bind=engine)


def check_db_connection() -> bool:
    """
    Test database connectivity.
    
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        >>> if check_db_connection():
        ...     print("Database connected!")
        ... else:
        ...     print("Database connection failed")
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
