"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.project import ExpertiseLevel, ProjectGoal, ProjectStatus, ProjectTone
from app.models.title import SearchIntent


# ============ Project Schemas ============


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    topic: str = Field(..., min_length=5, max_length=500)
    target_audience: str = Field(..., min_length=5, max_length=500)
    goal: ProjectGoal = ProjectGoal.SEO
    tone: ProjectTone = ProjectTone.AUTHORITATIVE
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    word_count_min: int = Field(1500, ge=500, le=10000)
    word_count_max: int = Field(3000, ge=500, le=20000)
    constraints: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: str
    topic: str
    target_audience: str
    goal: str  # Use str to avoid enum serialization issues
    tone: str
    expertise_level: str
    word_count_min: int
    word_count_max: int
    constraints: Optional[str]
    status: str
    selected_title_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""

    items: List[ProjectResponse]
    total: int
    page: int
    per_page: int


# ============ Title Schemas ============


class TitleResponse(BaseModel):
    """Schema for title response."""

    id: str
    title: str
    description: str
    search_intent: str  # Use str to avoid enum serialization issues
    difficulty: int
    is_selected: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TitleSelectRequest(BaseModel):
    """Schema for selecting a title."""

    title_id: str


class TitlesGeneratedResponse(BaseModel):
    """Schema for generated titles response."""

    project_id: str
    titles: List[TitleResponse]


# ============ Plan Schemas ============


class PlanSectionCreate(BaseModel):
    """Schema for creating/updating a plan section."""

    heading: str = Field(..., max_length=500)
    heading_level: int = Field(2, ge=1, le=6)
    key_points: List[str] = Field(default_factory=list)
    estimated_words: int = Field(300, ge=50, le=5000)
    is_locked: bool = False
    parent_id: Optional[str] = None


class PlanSectionResponse(BaseModel):
    """Schema for plan section response."""

    id: str
    heading: str
    heading_level: int
    key_points: List[str]
    suggested_sources: List[str]
    estimated_words: int
    order: int
    is_locked: bool
    parent_id: Optional[str]

    class Config:
        from_attributes = True


class PlanResponse(BaseModel):
    """Schema for plan response."""

    id: str
    project_id: str
    is_approved: bool
    total_estimated_words: int
    sections: List[PlanSectionResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanUpdateRequest(BaseModel):
    """Schema for updating plan sections."""

    sections: List[PlanSectionCreate]


# ============ Draft Schemas ============


class InsightScoreResponse(BaseModel):
    """Schema for I-N-S-I-G-H-T score response."""

    inspiring_score: float
    novel_score: float
    structured_score: float
    informative_score: float
    grounded_score: float
    helpful_score: float
    trustworthy_score: float
    overall_score: float
    primary_insight: Optional[str]
    feedback: List[str]
    suggestions: List[str]

    class Config:
        from_attributes = True


class DraftResponse(BaseModel):
    """Schema for draft response."""

    id: str
    project_id: str
    content_markdown: str
    content_html: Optional[str]
    word_count: int
    version: int
    is_current: bool
    is_approved: bool
    seo_title: Optional[str]
    meta_description: Optional[str]
    faq_schema: Optional[List[dict]]
    insight_score: Optional[InsightScoreResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftRewriteRequest(BaseModel):
    """Schema for requesting section rewrite."""

    section_id: Optional[str] = None
    instructions: str = Field(..., min_length=10, max_length=1000)
    tone_change: Optional[ProjectTone] = None


class DraftUpdateRequest(BaseModel):
    """Schema for manual draft update."""
    
    content_markdown: str = Field(..., min_length=1)


# ============ Execution Schemas ============


class AgentLogEntry(BaseModel):
    """Schema for agent log entry."""

    timestamp: str  # Use str for flexibility
    agent: str
    message: str
    level: Optional[str] = "info"  # info, success, warning, error
    step: Optional[str] = None
    status: Optional[str] = None
    latency_ms: Optional[int] = None
    tokens: Optional[int] = None


class ExecutionStatus(BaseModel):
    """Schema for execution status response."""

    project_id: str
    status: str  # Use str to avoid enum serialization issues
    current_agent: Optional[str]
    progress_percent: float
    logs: List[AgentLogEntry]
    sources_discovered: int
    confidence_scores: dict


# ============ Export Schemas ============


class ExportRequest(BaseModel):
    """Schema for export request."""

    format: str = Field("markdown", pattern="^(markdown|html|wordpress)$")
    include_metadata: bool = True


class ExportResponse(BaseModel):
    """Schema for export response."""

    content: str
    format: str
    seo_title: Optional[str]
    meta_description: Optional[str]
    faq_schema: Optional[List[dict]]
