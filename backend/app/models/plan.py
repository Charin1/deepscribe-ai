"""Blog plan and section database models."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Plan(Base):
    """Blog outline/plan model."""

    __tablename__ = "plans"

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
        unique=True,
    )
    
    # Plan status
    is_approved: Mapped[bool] = mapped_column(default=False)
    total_estimated_words: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="plan")
    sections: Mapped[List["PlanSection"]] = relationship(
        "PlanSection", back_populates="plan", cascade="all, delete-orphan",
        order_by="PlanSection.order"
    )

    def __repr__(self) -> str:
        return f"<Plan {self.id} for project {self.project_id}>"


class PlanSection(Base):
    """Individual section within a blog plan."""

    __tablename__ = "plan_sections"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Foreign key
    plan_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Section content
    heading: Mapped[str] = mapped_column(String(500), nullable=False)
    heading_level: Mapped[int] = mapped_column(Integer, default=2)  # H1, H2, H3
    key_points: Mapped[List[str]] = mapped_column(JSON, default=list)
    suggested_sources: Mapped[List[str]] = mapped_column(JSON, default=list)
    estimated_words: Mapped[int] = mapped_column(Integer, default=300)
    
    # Ordering and locking
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_locked: Mapped[bool] = mapped_column(default=False)
    
    # Parent section for nested structure
    parent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("plan_sections.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    plan: Mapped["Plan"] = relationship("Plan", back_populates="sections")
    children: Mapped[List["PlanSection"]] = relationship(
        "PlanSection", back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped[Optional["PlanSection"]] = relationship(
        "PlanSection", back_populates="children", remote_side=[id]
    )

    def __repr__(self) -> str:
        return f"<PlanSection {self.id}: {self.heading[:50]}>"
