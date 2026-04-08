"""Database configuration and session management"""

import os
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine, Session as SQLModelSession

# Database configuration - defaults to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./activities.db")

# Create engine with different settings based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session for dependency injection"""
    with SQLModelSession(engine) as session:
        yield session
