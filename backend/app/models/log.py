from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID

from app.core.database import Base

class ProjectLog(Base):
    """Log entry for project execution."""

    __tablename__ = "project_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    agent: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String, default="info")
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    
    def __repr__(self) -> str:
        return f"<Log {self.timestamp} {self.agent}: {self.message[:20]}...>"
