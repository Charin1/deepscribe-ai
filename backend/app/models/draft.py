"""Draft database models."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
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
    insight_score: Mapped[Optional["InsightScore"]] = relationship(
        "InsightScore", back_populates="draft", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Draft {self.id} v{self.version}>"


class InsightScore(Base):
    """I-N-S-I-G-H-T score breakdown for a draft."""

    __tablename__ = "insight_scores"

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
    
    # I-N-S-I-G-H-T scores (0-100)
    inspiring_score: Mapped[float] = mapped_column(Float, default=0.0)
    novel_score: Mapped[float] = mapped_column(Float, default=0.0)
    structured_score: Mapped[float] = mapped_column(Float, default=0.0)
    informative_score: Mapped[float] = mapped_column(Float, default=0.0)
    grounded_score: Mapped[float] = mapped_column(Float, default=0.0)
    helpful_score: Mapped[float] = mapped_column(Float, default=0.0)
    trustworthy_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Calculate average
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Insights and feedback
    primary_insight: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback: Mapped[List[str]] = mapped_column(JSON, default=list)
    suggestions: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Timestamps
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    draft: Mapped["Draft"] = relationship("Draft", back_populates="insight_score")

    def __repr__(self) -> str:
        return f"<InsightScore {self.id}: {self.overall_score:.1f}>"
