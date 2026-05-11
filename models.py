# Contains SQLAlchemy database models.
from database import Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# Todo table model.
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default = False)

    # Connects each todo to a specific user.
    owner_id = Column(Integer, ForeignKey("users.id"))

# User table model.
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index = True)
    email = Column(String, unique = True)
    username = Column(String, unique = True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default = True)
    role = Column(String)

    # Added later with an Alembic migration.
    phone_number = Column(String)
