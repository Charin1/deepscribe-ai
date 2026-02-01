"""Research sources and citations database models."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResearchSource(Base):
    """External research source model."""

    __tablename__ = "research_sources"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Foreign key - linked to project
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Section reference (optional)
    section_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("plan_sections.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Source details
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Content
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_facts: Mapped[List[str]] = mapped_column(JSON, default=list)
    quotes: Mapped[List[str]] = mapped_column(JSON, default=list)
    stats: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Scoring
    credibility_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    domain_authority: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    
    # Vector embedding reference
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<ResearchSource {self.id}: {self.domain}>"


class Citation(Base):
    """Citation linking content to sources."""

    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    
    # Foreign keys
    source_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("research_sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    draft_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("drafts.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Citation details
    cited_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    position_start: Mapped[int] = mapped_column(Integer, nullable=False)
    position_end: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Metadata
    citation_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Citation {self.citation_number} from source {self.source_id}>"
