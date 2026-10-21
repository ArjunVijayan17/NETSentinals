"""SQLite persistence via SQLAlchemy 2.0."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from ..config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class AnalysisRecord(Base):
    """One persisted CSV analysis session."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    benign_count: Mapped[int] = mapped_column(Integer, nullable=False)
    attack_count: Mapped[int] = mapped_column(Integer, nullable=False)
    attack_rate: Mapped[float] = mapped_column(Float, nullable=False)
    categories: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    row_results: Mapped[str] = mapped_column(Text, nullable=False)  # JSON

    def categories_dict(self) -> dict:
        return json.loads(self.categories)

    def row_results_list(self) -> list:
        return json.loads(self.row_results)


engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()
