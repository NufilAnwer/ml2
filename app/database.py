"""
Task 5 – Database Models (SQLAlchemy)
Every prediction request is logged permanently with:
  - image filename (sanitized), class decision, confidence, raw score,
    model version used, timestamp, request IP, file size, error (if any).
"""

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///visionguard.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    label = Column(String(50), nullable=False)           # "AI-Generated" or "Real"
    confidence = Column(Float, nullable=False)
    raw_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    model_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    client_ip = Column(String(50), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "label": self.label,
            "confidence": self.confidence,
            "raw_score": self.raw_score,
            "threshold": self.threshold,
            "model_path": self.model_path,
            "file_size_bytes": self.file_size_bytes,
            "client_ip": self.client_ip,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_db():
    """Create all tables. Call once at app startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session, ensure it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_prediction(db_session, filename: str, result: dict,
                   file_size: int = None, client_ip: str = None, error: str = None):
    """Insert one prediction record into the database."""
    record = PredictionLog(
        filename=filename,
        label=result.get("label", "ERROR"),
        confidence=result.get("confidence", 0.0),
        raw_score=result.get("raw_score", 0.0),
        threshold=result.get("threshold", 0.5),
        model_path=result.get("model_path", ""),
        file_size_bytes=file_size,
        client_ip=client_ip,
        error=error,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record

