"""Execution API endpoints for agent orchestration."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import DraftResponse, DraftRewriteRequest, ExecutionStatus, ExportRequest, ExportResponse
from app.api.execution_manager import (
    get_execution_state, 
    start_execution as start_sim_execution,
    get_logs_as_dicts,
)
from app.core.database import get_db
from app.models import Draft, Project, ProjectStatus

router = APIRouter(prefix="/projects/{project_id}", tags=["execution"])


@router.post("/run", response_model=ExecutionStatus)
async def start_execution(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Start the agent execution pipeline."""
    # Get project
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.plan))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    if project.status != ProjectStatus.PLAN_APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan must be approved before starting execution",
        )
    
    # Update status and start simulated execution
    project.status = ProjectStatus.RESEARCHING
    await db.commit()
    
    # Start the simulated execution (runs in background)
    start_sim_execution(project_id, topic=project.topic)
    
    return {
        "project_id": project_id,
        "status": "researching",
        "current_agent": "ResearchAgent",
        "progress_percent": 0.0,
        "logs": [],
        "sources_discovered": 0,
        "confidence_scores": {},
    }


@router.post("/restart", response_model=ExecutionStatus)
async def restart_execution(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Restart the agent execution pipeline (for debugging/testing)."""
    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Start the simulated execution (runs in background)
    start_sim_execution(project_id, topic=project.topic)
    
    return {
        "project_id": project_id,
        "status": "researching",
        "current_agent": "ResearchAgent",
        "progress_percent": 0.0,
        "logs": [{"timestamp": "", "agent": "System", "message": "🔄 Execution restarted", "level": "info"}],
        "sources_discovered": 0,
        "confidence_scores": {},
    }


@router.get("/status", response_model=ExecutionStatus)
async def get_execution_status(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get current execution status."""
    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Check if we have an active simulated execution
    state = get_execution_state(project_id)
    
    if state:
        # If execution is complete, create draft if it doesn't exist
        if state.is_complete and state.status == "draft_ready":
            # Draft creation is now handled by the execution pipeline
            pass
        
        # Return real-time state from execution manager
        return {
            "project_id": project_id,
            "status": state.status,
            "current_agent": state.current_agent,
            "progress_percent": state.progress_percent,
            "logs": get_logs_as_dicts(state),
            "sources_discovered": state.sources_discovered,
            "confidence_scores": {},
        }
    
    current_agent = None
    if project.status == ProjectStatus.RESEARCHING:
        current_agent = "ResearchAgent"
    elif project.status == ProjectStatus.WRITING:
        current_agent = "WriterAgent"
    elif project.status == ProjectStatus.EDITING:
        current_agent = "EditorAgent"
    
    # Status progress mapping
    status_progress = {
        ProjectStatus.CREATED: 0,
        ProjectStatus.TITLES_GENERATED: 10,
        ProjectStatus.TITLE_SELECTED: 20,
        ProjectStatus.PLAN_GENERATED: 30,
        ProjectStatus.PLAN_APPROVED: 40,
        ProjectStatus.RESEARCHING: 50,
        ProjectStatus.WRITING: 70,
        ProjectStatus.EDITING: 90,
        ProjectStatus.DRAFT_READY: 100,
        ProjectStatus.PUBLISHED: 100,
        ProjectStatus.FAILED: 0,
    }
    
    return {
        "project_id": project_id,
        "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
        "current_agent": current_agent,
        "progress_percent": status_progress.get(project.status, 0),
        "logs": [],
        "sources_discovered": 0,
        "confidence_scores": {},
    }



@router.get("/logs")
async def get_execution_logs(
    project_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get agent execution logs."""
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # TODO: Fetch logs from Redis or structured logging storage
    return {
        "project_id": project_id,
        "logs": [],
        "total": 0,
    }


@router.get("/result", response_model=DraftResponse)
async def get_result(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the current draft result."""
    # Get current draft
    result = await db.execute(
        select(Draft)
        .options(selectinload(Draft.insight_score))
        .where(Draft.project_id == project_id, Draft.is_current == True)
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No draft found for project {project_id}",
        )
    
    # Serialize draft to dict
    return {
        "id": str(draft.id),
        "project_id": str(draft.project_id),
        "content_markdown": draft.content_markdown,
        "content_html": draft.content_html,
        "word_count": draft.word_count,
        "version": draft.version,
        "is_current": draft.is_current,
        "is_approved": draft.is_approved,
        "seo_title": draft.seo_title,
        "meta_description": draft.meta_description,
        "faq_schema": draft.faq_schema,
        "insight_score": draft.insight_score,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at,
    }


@router.post("/rewrite", response_model=DraftResponse)
async def request_rewrite(
    project_id: str,
    data: DraftRewriteRequest,
    db: AsyncSession = Depends(get_db),
) -> Draft:
    """Request a section rewrite or tone change."""
    # Get current draft
    result = await db.execute(
        select(Draft)
        .options(selectinload(Draft.insight_score))
        .where(Draft.project_id == project_id, Draft.is_current == True)
    )
    current_draft = result.scalar_one_or_none()
    
    if not current_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No draft found for project {project_id}",
        )
    
    # TODO: Trigger rewrite with CrewAI Editor Agent
    # For now, return current draft
    return current_draft


@router.post("/approve", response_model=DraftResponse)
async def approve_draft(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> Draft:
    """Approve the current draft."""
    # Get current draft and project
    result = await db.execute(
        select(Draft)
        .options(selectinload(Draft.insight_score))
        .where(Draft.project_id == project_id, Draft.is_current == True)
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No draft found for project {project_id}",
        )
    
    # Update draft and project status
    draft.is_approved = True
    
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one()
    project.status = ProjectStatus.DRAFT_READY
    
    await db.commit()
    return draft


@router.post("/export", response_model=ExportResponse)
async def export_draft(
    project_id: str,
    data: ExportRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Export the draft in specified format."""
    # Get approved draft
    result = await db.execute(
        select(Draft)
        .where(Draft.project_id == project_id, Draft.is_current == True)
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No draft found for project {project_id}",
        )
    
    # Format content based on request
    content = draft.content_markdown
    
    if data.format == "html":
        # TODO: Convert markdown to HTML
        content = draft.content_html or f"<html><body>{content}</body></html>"
    elif data.format == "wordpress":
        # TODO: Format for WordPress
        content = draft.content_html or content
    
    response = {
        "content": content,
        "format": data.format,
    }
    
    if data.include_metadata:
        response["seo_title"] = draft.seo_title
        response["meta_description"] = draft.meta_description
        response["faq_schema"] = draft.faq_schema
    
    return response
