# Contains the database connection and session configuration.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_gemini.db"

# Creates the database engine.
# check_same_thread=False is needed for SQLite when used with FastAPI.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}

)
# Creates database sessions.
SessionLocal = sessionmaker(autocommit = False, autoflush=False,bind = engine)
# Base class for SQLAlchemy models.
Base = declarative_base()