"""
Execution manager for simulating AI agent execution with progress.
This provides a mock implementation that shows progress in the UI.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import random

@dataclass
class AgentLog:
    """A single log entry from an agent."""
    timestamp: str
    agent: str
    message: str
    level: str = "info"  # info, success, warning, error

@dataclass  
class ExecutionState:
    """State of an execution for a project."""
    project_id: str
    status: str = "researching"
    current_agent: str = "ResearchAgent"
    progress_percent: float = 0.0
    logs: List[AgentLog] = field(default_factory=list)
    sources_discovered: int = 0
    is_complete: bool = False

# In-memory storage for execution states
_execution_states: Dict[str, ExecutionState] = {}
_execution_tasks: Dict[str, asyncio.Task] = {}


def get_execution_state(project_id: str) -> Optional[ExecutionState]:
    """Get the current execution state for a project."""
    return _execution_states.get(project_id)


async def add_log(state: ExecutionState, agent: str, message: str, level: str = "info"):
    """Add a log entry to the execution state and database."""
    # Memory
    log = AgentLog(
        timestamp=datetime.now().isoformat(),
        agent=agent,
        message=message,
        level=level
    )
    state.logs.append(log)
    # Keep only last 100 logs
    if len(state.logs) > 100:
        state.logs = state.logs[-100:]
        
    # Database persistence
    try:
        from app.core.database import AsyncSessionLocal
        from app.models.log import ProjectLog
        
        async with AsyncSessionLocal() as db:
            db_log = ProjectLog(
                project_id=state.project_id,
                agent=agent,
                message=message,
                level=level
            )
            db.add(db_log)
            await db.commit()
    except Exception as e:
        print(f"Failed to persist log: {e}")


async def run_pipeline(project_id: str, topic: str):
    """Run the real AI agent execution pipeline."""
    # Retrieve state initialized in start_execution
    state = _execution_states.get(project_id)
    if not state:
        # This case should ideally not happen if start_execution is always called first
        # but provides a fallback to prevent errors.
        state = ExecutionState(project_id=project_id)
        _execution_states[project_id] = state

    # Callback for progress updates
    async def on_progress(agent: str, message: str, percent: float):
        level = "info"
        if "complete" in message.lower() or "finished" in message.lower():
            level = "success"
        elif "error" in message.lower() or "fail" in message.lower():
            level = "error"
            
        await add_log(state, agent.capitalize(), message, level)
        state.current_agent = agent
        state.progress_percent = percent
        # Map agent names to status
        if agent == "research":
            state.status = "researching"
        elif agent == "writing":
            state.status = "writing"
        elif agent == "editing":
            state.status = "editing"
        
        # Simulate some delay for readable UI updates
        await asyncio.sleep(0.5)

    try:
        # Sync settings to os.environ so libraries (CrewAI/LangChain) can find keys
        # This respects the .env file as loaded by Settings
        from app.core import get_settings
        import os
        settings = get_settings()
        
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.groq_api_key:
            os.environ["GROQ_API_KEY"] = settings.groq_api_key
        if settings.serper_api_key:
            os.environ["SERPER_API_KEY"] = settings.serper_api_key
            
        from app.agents.crew import DeepScribePipeline
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models import Project, Draft, ProjectStatus, Plan, InsightScore, ProjectLog
        from uuid import uuid4

        await add_log(state, "System", "🚀 Starting DeepScribe AI Pipeline...", "info")
        
        # 1. Fetch project and plan from DB
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Project)
                .options(selectinload(Project.plan).selectinload(Plan.sections))
                .options(selectinload(Project.titles))
                .where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            
            if not project or not project.plan:
                raise Exception("Project or plan not found")
            
            # Prepare input data
            selected_title = next((t for t in project.titles if t.is_selected), None)
            title_text = selected_title.title if selected_title else project.topic
            
            sections_data = [
                {
                    "heading": s.heading,
                    "key_points": s.key_points,
                    "estimated_words": s.estimated_words
                }
                for s in sorted(project.plan.sections, key=lambda x: x.order)
            ]
            
            # 2. Run LangChain Pipeline
            pipeline = DeepScribePipeline()
            result = await pipeline.run_full_pipeline(
                project_id=project_id,
                topic=project.topic,
                target_audience=project.target_audience,
                goal=project.goal.value if hasattr(project.goal, 'value') else str(project.goal),
                tone=project.tone.value if hasattr(project.tone, 'value') else str(project.tone),
                expertise_level=project.expertise_level.value if hasattr(project.expertise_level, 'value') else str(project.expertise_level),
                title=title_text,
                sections=sections_data,
                on_progress=on_progress
            )
            
            # 3. Save Draft to DB
            content = result["content"]
            word_count = len(content.split())
            
            # Check if previous current draft exists and update it
            existing_result = await db.execute(
                select(Draft).where(Draft.project_id == project_id, Draft.is_current == True)
            )
            existing_draft = existing_result.scalar_one_or_none()
            
            if existing_draft:
                existing_draft.is_current = False
                
            new_draft = Draft(
                id=str(uuid4()),
                project_id=project_id,
                content_markdown=content,
                # Simple HTML conversion (could be improved)
                content_html=f"<div>{content}</div>",
                word_count=word_count,
                version=(existing_draft.version + 1) if existing_draft else 1,
                is_current=True,
                is_approved=False,
                seo_title=f"{title_text}",
                meta_description=f"DeepScribe generated content for {project.topic}",
            )
            db.add(new_draft)
            
            # Update project status
            project.status = ProjectStatus.DRAFT_READY
            db.add(new_draft)
            await db.flush() # Flush to get new_draft.id

            # 4. Save Insight Score
            if "insight_assessment" in result:
                assessment = result["insight_assessment"]
                # Assuming assessment is a dict or Pydantic object
                # If it's a Pydantic object, access attributes, if dict access keys.
                # The pipeline likely returns a dict or object. Let's assume dict for safety or convert.
                
                # Check if it's an object and convert to dict if needed
                if hasattr(assessment, "dict"):
                    assessment_data = assessment.dict()
                else:
                    assessment_data = assessment

                insight_score = InsightScore(
                    draft_id=new_draft.id,
                    inspiring_score=assessment_data.get("insight_score_inspiring", 0),
                    novel_score=assessment_data.get("insight_score_novel", 0),
                    structured_score=assessment_data.get("insight_score_structured", 0),
                    informative_score=assessment_data.get("insight_score_informative", 0),
                    grounded_score=assessment_data.get("insight_score_grounded", 0),
                    helpful_score=assessment_data.get("insight_score_helpful", 0),
                    trustworthy_score=assessment_data.get("insight_score_trustworthy", 0),
                    overall_score=(
                        assessment_data.get("insight_score_inspiring", 0) +
                        assessment_data.get("insight_score_novel", 0) +
                        assessment_data.get("insight_score_structured", 0) +
                        assessment_data.get("insight_score_informative", 0) +
                        assessment_data.get("insight_score_grounded", 0) +
                        assessment_data.get("insight_score_helpful", 0) +
                        assessment_data.get("insight_score_trustworthy", 0)
                    ) / 7.0,
                    primary_insight=assessment_data.get("primary_insight", ""),
                    feedback=assessment_data.get("feedback", []),
                    suggestions=assessment_data.get("suggestions", []),
                )
                db.add(insight_score)

            await db.commit()
            
            await add_log(state, "System", f"🎉 Draft saved ({word_count} words)!", "success")
            state.status = "draft_ready"
            state.progress_percent = 100
            state.is_complete = True

    except asyncio.CancelledError:
        await add_log(state, "System", "⚠️ Execution cancelled", "warning")
        state.status = "failed"
        state.is_complete = True
        raise
    except Exception as e:
        import traceback
        traceback.print_exc() # Print to server logs
        await add_log(state, "System", f"❌ Error: {str(e)}", "error")
        state.status = "failed"
        state.is_complete = True
        
        # Try to update project status in DB to failed
        try:
            from app.core.database import AsyncSessionLocal
            from app.models import Project, ProjectStatus
            
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Project).where(Project.id == project_id))
                project = result.scalar_one_or_none()
                if project:
                    project.status = ProjectStatus.FAILED
                    await db.commit()
        except Exception as db_err:
            print(f"Failed to update project status to FAILED: {db_err}")


async def start_execution(project_id: str, topic: str = "AI Topic") -> ExecutionState:
    """Start execution for a project (non-blocking)."""
    # Cancel any existing execution
    if project_id in _execution_tasks:
        _execution_tasks[project_id].cancel()
    
    # Create new execution task running the REAL pipeline
    # Reset state immediately to avoid race conditions
    _execution_states[project_id] = ExecutionState(project_id=project_id, logs=[
        AgentLog(datetime.now().isoformat(), "System", "🔄 Restarting execution...", "info")
    ])
    
    task = asyncio.create_task(run_pipeline(project_id, topic))
    _execution_tasks[project_id] = task
    
    # Return initial state
    return _execution_states.get(project_id)


def get_logs_as_dicts(state: ExecutionState) -> List[dict]:
    """Convert logs to dict format for API response."""
    return [
        {
            "timestamp": log.timestamp,
            "agent": log.agent,
            "message": log.message,
            "level": log.level,
        }
        for log in state.logs
    ]
