"""Draft and EEAT score database models."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Draft(Base):
    """Generated blog draft model."""

    __tablename__ = "drafts"

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
    
    # Draft content
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Version tracking
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_current: Mapped[bool] = mapped_column(default=True)
    is_approved: Mapped[bool] = mapped_column(default=False)
    
    # SEO metadata
    seo_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    faq_schema: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="drafts")
    eeat_score: Mapped[Optional["EEATScore"]] = relationship(
        "EEATScore", back_populates="draft", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Draft {self.id} v{self.version}>"


class EEATScore(Base):
    """E-E-A-T score breakdown for a draft."""

    __tablename__ = "eeat_scores"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Foreign key
    draft_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("drafts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # E-E-A-T scores (0-100)
    experience_score: Mapped[float] = mapped_column(Float, default=0.0)
    expertise_score: Mapped[float] = mapped_column(Float, default=0.0)
    authority_score: Mapped[float] = mapped_column(Float, default=0.0)
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Overall score
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Feedback and suggestions
    experience_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expertise_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    authority_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trust_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Weak sections flagged
    weak_sections: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Timestamps
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    draft: Mapped["Draft"] = relationship("Draft", back_populates="eeat_score")

    def __repr__(self) -> str:
        return f"<EEATScore {self.id}: {self.overall_score:.1f}>"
