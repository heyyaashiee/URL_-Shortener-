"""
Database schema (Step 1 of the roadmap).

Three tables:
- User   : people who sign up and create short links
- URL    : the mapping between a short_code and the original long URL
- Click  : one row per redirect, used to power the analytics dashboard later
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # One user can create many short links
    urls = relationship("URL", back_populates="owner", cascade="all, delete-orphan")


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)

    # The short code shown in the shortened link, e.g. "aZ9kLp"
    short_code = Column(String(10), unique=True, index=True, nullable=False)

    original_url = Column(String, nullable=False)

    # Nullable because you may want to allow anonymous shortening later
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    owner = relationship("User", back_populates="urls")
    clicks = relationship("Click", back_populates="url", cascade="all, delete-orphan")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)

    clicked_at = Column(DateTime(timezone=True), default=utcnow)
    referrer = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    url = relationship("URL", back_populates="clicks")

# Note: short-code generation now lives in app/shortener.py
# (proper base62 encoding + collision checks against this table)
