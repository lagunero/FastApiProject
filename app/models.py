import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(LargeBinary, primary_key=True, default=lambda: uuid.uuid4().bytes)
    user_name = Column(String)
    password = Column(String)
    role = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
