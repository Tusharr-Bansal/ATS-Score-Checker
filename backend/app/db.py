"""Database setup (PostgreSQL in Docker/production; SQLite works for quick local runs)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from .config import settings

url = settings.database_url
if url.startswith("postgres://"):  # Heroku/Render style URLs
    url = url.replace("postgres://", "postgresql+psycopg://", 1)
elif url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(url, pool_pre_ping=True,
                       connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

JSONType = JSON().with_variant(JSONB(), "postgresql")


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), default="")
    raw_text: Mapped[str] = mapped_column(Text)
    data: Mapped[dict] = mapped_column(JSONType)            # JDData
    extractor: Mapped[str] = mapped_column(String(20), default="rules")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    candidates: Mapped[list["Candidate"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(300))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="queued")  # queued|processing|done|error
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSONType, nullable=True)     # ResumeData
    extractor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    result: Mapped[dict | None] = mapped_column(JSONType, nullable=True)   # full match explanation
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    job: Mapped[Job] = relationship(back_populates="candidates")


def init_db():
    Base.metadata.create_all(engine)
