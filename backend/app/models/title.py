"""Title database model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class SearchIntent(str, enum.Enum):
    """Search intent classification."""

    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class Title(Base):
    """Generated title model with metadata."""

    __tablename__ = "titles"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Foreign key
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Title content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    search_intent: Mapped[SearchIntent] = mapped_column(
        Enum(SearchIntent), default=SearchIntent.INFORMATIONAL
    )
    difficulty: Mapped[int] = mapped_column(Integer, default=5)  # 1-10 scale
    
    # Selection
    is_selected: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="titles")

    def __repr__(self) -> str:
        return f"<Title {self.id}: {self.title[:50]}>"
