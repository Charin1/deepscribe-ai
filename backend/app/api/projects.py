"""Project API endpoints."""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import (
    PlanResponse,
    PlanUpdateRequest,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    TitleSelectRequest,
    TitlesGeneratedResponse,
)
from app.core.database import get_db
from app.models import Draft, Plan, PlanSection, Project, ProjectStatus, Title

router = APIRouter(prefix="/projects", tags=["projects"])


def serialize_project(project: Project) -> dict:
    """Serialize a Project model to dict with enum values as strings."""
    return {
        "id": project.id,
        "topic": project.topic,
        "target_audience": project.target_audience,
        "goal": project.goal.value if hasattr(project.goal, 'value') else str(project.goal),
        "tone": project.tone.value if hasattr(project.tone, 'value') else str(project.tone),
        "expertise_level": project.expertise_level.value if hasattr(project.expertise_level, 'value') else str(project.expertise_level),
        "word_count_min": project.word_count_min,
        "word_count_max": project.word_count_max,
        "constraints": project.constraints,
        "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
        "selected_title_id": project.selected_title_id,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Create a new blog project."""
    project = Project(
        id=str(uuid4()),
        topic=data.topic,
        target_audience=data.target_audience,
        goal=data.goal,
        tone=data.tone,
        expertise_level=data.expertise_level,
        word_count_min=data.word_count_min,
        word_count_max=data.word_count_max,
        constraints=data.constraints,
        status=ProjectStatus.CREATED,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return serialize_project(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all projects with pagination."""
    offset = (page - 1) * per_page
    
    # Get total count
    count_result = await db.execute(select(func.count(Project.id)))
    total = count_result.scalar() or 0
    
    # Get paginated projects
    result = await db.execute(
        select(Project)
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    projects = result.scalars().all()
    
    return {
        "items": [serialize_project(p) for p in projects],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Get a project by ID."""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    return serialize_project(project)


@router.get("/{project_id}/titles", response_model=TitlesGeneratedResponse)
async def get_titles(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get all titles for a project."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.titles))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    return {
        "project_id": project_id,
        "titles": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "search_intent": t.search_intent.value if hasattr(t.search_intent, 'value') else str(t.search_intent),
                "difficulty": t.difficulty,
                "is_selected": t.is_selected,
                "created_at": t.created_at,
            }
            for t in project.titles
        ],
    }


@router.post("/{project_id}/generate-titles", response_model=TitlesGeneratedResponse)
async def generate_titles(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate title suggestions for a project."""
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
    
    # TODO: Integrate with CrewAI Title Strategist Agent
    # For now, return placeholder titles
    placeholder_titles = [
        {
            "title": f"The Ultimate Guide to {project.topic}",
            "description": "A comprehensive overview covering all essential aspects.",
            "search_intent": "informational",
            "difficulty": 6,
        },
        {
            "title": f"How to Master {project.topic} in 2024",
            "description": "Step-by-step guide for achieving expertise.",
            "search_intent": "informational",
            "difficulty": 5,
        },
        {
            "title": f"{project.topic}: What Experts Don't Tell You",
            "description": "Insider knowledge and hidden strategies revealed.",
            "search_intent": "informational",
            "difficulty": 7,
        },
        {
            "title": f"10 Essential {project.topic} Tips for {project.target_audience}",
            "description": "Targeted advice for your specific audience.",
            "search_intent": "informational",
            "difficulty": 4,
        },
        {
            "title": f"Why {project.topic} Matters More Than Ever",
            "description": "Exploring the growing importance and impact.",
            "search_intent": "commercial",
            "difficulty": 5,
        },
    ]
    
    titles = []
    for i, t_data in enumerate(placeholder_titles):
        title = Title(
            id=str(uuid4()),
            project_id=project_id,
            title=t_data["title"],
            description=t_data["description"],
            search_intent=t_data["search_intent"],
            difficulty=t_data["difficulty"],
        )
        db.add(title)
        titles.append(title)
    
    project.status = ProjectStatus.TITLES_GENERATED
    await db.commit()
    
    return {
        "project_id": project_id,
        "titles": titles,
    }


@router.post("/{project_id}/select-title", response_model=ProjectResponse)
async def select_title(
    project_id: str,
    data: TitleSelectRequest,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Select a title for the project."""
    # Get project with titles
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.titles))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Find and select the title
    title_found = False
    for title in project.titles:
        if title.id == data.title_id:
            title.is_selected = True
            project.selected_title_id = title.id
            title_found = True
        else:
            title.is_selected = False
    
    if not title_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title {data.title_id} not found in project",
        )
    
    project.status = ProjectStatus.TITLE_SELECTED
    response_data = serialize_project(project)
    await db.commit()
    
    return response_data


@router.get("/{project_id}/plan", response_model=PlanResponse)
async def get_plan(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the plan for a project."""
    result = await db.execute(
        select(Plan)
        .options(selectinload(Plan.sections))
        .where(Plan.project_id == project_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan for project {project_id} not found",
        )
    
    # Serialize sections with proper order
    sections = sorted(plan.sections, key=lambda s: s.order)
    return {
        "id": plan.id,
        "project_id": plan.project_id,
        "is_approved": plan.is_approved,
        "total_estimated_words": plan.total_estimated_words,
        "sections": [
            {
                "id": s.id,
                "heading": s.heading,
                "heading_level": s.heading_level,
                "key_points": s.key_points or [],
                "suggested_sources": s.suggested_sources or [],
                "estimated_words": s.estimated_words,
                "order": s.order,
                "is_locked": s.is_locked,
                "parent_id": s.parent_id,
            }
            for s in sections
        ],
        "created_at": plan.created_at,
        "updated_at": plan.updated_at,
    }


@router.post("/{project_id}/generate-plan", response_model=PlanResponse)
async def generate_plan(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """Generate a blog outline/plan for the project."""
    # Get project
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.titles))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    if project.status not in [ProjectStatus.TITLE_SELECTED, ProjectStatus.PLAN_GENERATED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a title before generating a plan",
        )
    
    # Get selected title
    selected_title = next((t for t in project.titles if t.is_selected), None)
    title_text = selected_title.title if selected_title else project.topic
    
    # Check for existing plan and delete if exists
    existing_plan_result = await db.execute(
        select(Plan).where(Plan.project_id == project_id)
    )
    existing_plan = existing_plan_result.scalar_one_or_none()
    
    if existing_plan:
        # Delete sections first (cascade should handle this but explicit is safer)
        await db.execute(delete(PlanSection).where(PlanSection.plan_id == existing_plan.id))
        await db.delete(existing_plan)
        await db.commit()
    
    # TODO: Integrate with CrewAI Content Planner Agent
    # For now, return placeholder plan
    plan = Plan(
        id=str(uuid4()),
        project_id=project_id,
        is_approved=False,
        total_estimated_words=project.word_count_min,
    )
    db.add(plan)
    await db.commit()
    
    # Create placeholder sections
    sections_data = [
        {"heading": "Introduction", "level": 2, "words": 200, "points": ["Hook the reader", "Preview main points"]},
        {"heading": f"Understanding {project.topic}", "level": 2, "words": 400, "points": ["Core concepts", "Key terminology"]},
        {"heading": "Key Benefits and Advantages", "level": 2, "words": 350, "points": ["Main benefits", "Real-world applications"]},
        {"heading": "Best Practices", "level": 2, "words": 400, "points": ["Industry standards", "Expert recommendations"]},
        {"heading": "Common Challenges and Solutions", "level": 2, "words": 300, "points": ["Typical obstacles", "Proven solutions"]},
        {"heading": "Conclusion", "level": 2, "words": 150, "points": ["Summary", "Call to action"]},
    ]
    
    for i, s_data in enumerate(sections_data):
        section = PlanSection(
            id=str(uuid4()),
            plan_id=plan.id,
            heading=s_data["heading"],
            heading_level=s_data["level"],
            key_points=s_data["points"],
            estimated_words=s_data["words"],
            order=i,
        )
        db.add(section)
    
    project.status = ProjectStatus.PLAN_GENERATED
    await db.commit()
    
    # Reload plan with sections
    result = await db.execute(
        select(Plan)
        .options(selectinload(Plan.sections))
        .where(Plan.id == plan.id)
    )
    return result.scalar_one()


@router.put("/{project_id}/plan", response_model=PlanResponse)
async def update_plan(
    project_id: str,
    data: PlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> Plan:
    """Update plan sections."""
    # Get plan with sections
    result = await db.execute(
        select(Plan)
        .options(selectinload(Plan.sections))
        .where(Plan.project_id == project_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan for project {project_id} not found",
        )
    
    # Delete existing non-locked sections
    for section in plan.sections:
        if not section.is_locked:
            await db.delete(section)
    
    # Add new sections
    total_words = 0
    for i, s_data in enumerate(data.sections):
        section = PlanSection(
            id=str(uuid4()),
            plan_id=plan.id,
            heading=s_data.heading,
            heading_level=s_data.heading_level,
            key_points=s_data.key_points,
            estimated_words=s_data.estimated_words,
            order=i,
            is_locked=s_data.is_locked,
            parent_id=s_data.parent_id,
        )
        db.add(section)
        total_words += s_data.estimated_words
    
    plan.total_estimated_words = total_words
    await db.commit()
    
    # Reload plan with sections
    result = await db.execute(
        select(Plan)
        .options(selectinload(Plan.sections))
        .where(Plan.id == plan.id)
    )
    return result.scalar_one()


@router.post("/{project_id}/approve-plan", response_model=ProjectResponse)
async def approve_plan(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Approve the plan and start research phase."""
    # Get project and plan
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
    
    if not project.plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No plan exists for this project",
        )
    
    project.plan.is_approved = True
    project.status = ProjectStatus.PLAN_APPROVED
    response_data = serialize_project(project)
    await db.commit()
    
    return response_data


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project and all associated data."""
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    # Cascade delete 
    # Delete drafts
    await db.execute(delete(Draft).where(Draft.project_id == project_id))

    # Delete plan sections and plan
    plan_result = await db.execute(
        select(Plan).where(Plan.project_id == project_id)
    )
    plan = plan_result.scalar_one_or_none()
    if plan:
        await db.execute(delete(PlanSection).where(PlanSection.plan_id == plan.id))
        await db.delete(plan)
        
    # Delete titles
    await db.execute(delete(Title).where(Title.project_id == project_id))
    
    # Delete project
    await db.delete(project)
    await db.commit()
