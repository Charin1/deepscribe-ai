"""Project database model."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.draft import Draft
    from app.models.plan import Plan
    from app.models.title import Title


class ProjectStatus(str, enum.Enum):
    """Project workflow status."""

    CREATED = "created"
    TITLES_GENERATED = "titles_generated"
    TITLE_SELECTED = "title_selected"
    PLAN_GENERATED = "plan_generated"
    PLAN_APPROVED = "plan_approved"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    DRAFT_READY = "draft_ready"
    PUBLISHED = "published"
    FAILED = "failed"


class ProjectGoal(str, enum.Enum):
    """Content goal types."""

    SEO = "seo"
    THOUGHT_LEADERSHIP = "thought_leadership"
    TECHNICAL = "technical"
    MARKETING = "marketing"


class ProjectTone(str, enum.Enum):
    """Content tone types."""

    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"
    PERSUASIVE = "persuasive"


class ExpertiseLevel(str, enum.Enum):
    """Target expertise level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class Project(Base):
    """Project model representing a blog post creation workflow."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Core fields
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[ProjectGoal] = mapped_column(Enum(ProjectGoal), default=ProjectGoal.SEO)
    tone: Mapped[ProjectTone] = mapped_column(Enum(ProjectTone), default=ProjectTone.AUTHORITATIVE)
    expertise_level: Mapped[ExpertiseLevel] = mapped_column(
        Enum(ExpertiseLevel), default=ExpertiseLevel.INTERMEDIATE
    )
    
    # Constraints
    word_count_min: Mapped[int] = mapped_column(default=1500)
    word_count_max: Mapped[int] = mapped_column(default=3000)
    constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.CREATED
    )
    selected_title_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    titles: Mapped[List["Title"]] = relationship(
        "Title", back_populates="project", cascade="all, delete-orphan"
    )
    plan: Mapped[Optional["Plan"]] = relationship(
        "Plan", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    drafts: Mapped[List["Draft"]] = relationship(
        "Draft", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project {self.id}: {self.topic[:50]}>"
