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
from app.core.llm import get_llm
from app.core.retry import invoke_with_retry
from app.agents.title_strategist import create_title_chain
from app.agents.content_planner import create_planner_chain

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
    
    # Integrate with CrewAI Title Strategist Agent
    llm = get_llm(temperature=0.7)
    title_chain = create_title_chain(llm)

    try:
        result = await invoke_with_retry(title_chain, {
            "topic": project.topic,
            "target_audience": project.target_audience,
            "goal": project.goal.value if hasattr(project.goal, 'value') else str(project.goal),
            "tone": project.tone.value if hasattr(project.tone, 'value') else str(project.tone),
            "expertise_level": project.expertise_level.value if hasattr(project.expertise_level, 'value') else str(project.expertise_level),
        })
        
        titles_suggestions = result.titles
    except Exception as e:
        print(f"Title generation failed: {e}")
        # Fallback to placeholders if LLM fails
        titles_suggestions = [
            type('obj', (object,), {
                "title": f"The Ultimate Guide to {project.topic}",
                "description": "A comprehensive overview covering all essential aspects.",
                "search_intent": "informational",
                "difficulty": 5
            }),
            type('obj', (object,), {
                 "title": f"{project.topic} Explained",
                 "description": "Everything you need to know.",
                 "search_intent": "informational",
                 "difficulty": 4
            })
        ]

    titles = []
    for t_data in titles_suggestions:
        # Check if t_data is object or dict (Pydantic model vs fallback)
        title_text = t_data.title if hasattr(t_data, 'title') else t_data['title']
        description = t_data.description if hasattr(t_data, 'description') else t_data['description']
        search_intent = t_data.search_intent if hasattr(t_data, 'search_intent') else t_data['search_intent']
        difficulty = t_data.difficulty if hasattr(t_data, 'difficulty') else t_data['difficulty']

        title = Title(
            id=str(uuid4()),
            project_id=project_id,
            title=title_text,
            description=description,
            search_intent=search_intent,
            difficulty=difficulty,
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
    
    # Integrate with CrewAI Content Planner Agent
    llm = get_llm(temperature=0.7)
    planner_chain = create_planner_chain(llm)

    try:
        plan_result = await invoke_with_retry(planner_chain, {
            "title": title_text,
            "topic": project.topic,
            "target_audience": project.target_audience,
            "goal": project.goal.value if hasattr(project.goal, 'value') else str(project.goal),
            "tone": project.tone.value if hasattr(project.tone, 'value') else str(project.tone),
            "expertise_level": project.expertise_level.value if hasattr(project.expertise_level, 'value') else str(project.expertise_level),
            "word_count_min": project.word_count_min,
            "word_count_max": project.word_count_max
        })
        
        sections_data = plan_result.sections
    except Exception as e:
        print(f"Plan generation failed: {e}")
        # Fallback to placeholders if LLM fails
        sections_data = [
            type('obj', (object,), {"heading": "Introduction", "heading_level": 2, "estimated_words": 200, "key_points": ["Hook the reader", "Preview main points"]}),
            type('obj', (object,), {"heading": f"Understanding {project.topic}", "heading_level": 2, "estimated_words": 400, "key_points": ["Core concepts", "Key terminology"]}),
            type('obj', (object,), {"heading": "Key Benefits", "heading_level": 2, "estimated_words": 350, "key_points": ["Main benefits"]}),
            type('obj', (object,), {"heading": "Conclusion", "heading_level": 2, "estimated_words": 150, "key_points": ["Summary", "CTA"]}),
        ]

    plan = Plan(
        id=str(uuid4()),
        project_id=project_id,
        is_approved=False,
        total_estimated_words=project.word_count_min,
    )
    db.add(plan)
    await db.commit()
    
    # Create sections
    for i, s_data in enumerate(sections_data):
        # Handle Pydantic model vs fallback object
        heading = s_data.heading if hasattr(s_data, 'heading') else s_data.heading
        level = s_data.heading_level if hasattr(s_data, 'heading_level') else 2 # default to 2 if missing
        # Some models might use 'section_type' or 'level', let's check attributes safely
        if hasattr(s_data, 'section_type'):
            # simple mapping if needed, or assume H2
            pass
            
        points = s_data.key_points if hasattr(s_data, 'key_points') else getattr(s_data, 'key_points', [])
        words = s_data.estimated_words if hasattr(s_data, 'estimated_words') else getattr(s_data, 'estimated_words', 200)

        section = PlanSection(
            id=str(uuid4()),
            plan_id=plan.id,
            heading=heading,
            heading_level=level, 
            key_points=points,
            estimated_words=words,
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
