"""Pipeline Orchestration - Manages the full content creation workflow."""

import asyncio
from typing import List

from app.agents.title_strategist import create_title_chain
from app.agents.content_planner import create_planner_chain
from app.agents.researcher import create_researcher_chain
from app.agents.writer import create_writer_chain

from app.agents.insight_validator import create_insight_validator_chain
from app.agents.editor import create_editor_chain
from app.core import get_logger, get_settings
from app.core.retry import invoke_with_retry

settings = get_settings()
logger = get_logger(__name__)

def summarize_sources_text(sources_list) -> str:
    """Compact specific sources list for writer."""
    if not sources_list:
        return "No specific sources."
    # sources_list is a list of Source objects
    return "\n".join([f"- {s.title} ({s.url})" for s in sources_list])

def summarize_all_research(research_results) -> str:
    """Compact all research into a minimal format for editor."""
    summary = []
    for res in research_results:
        summary.append(f"## {res.heading}")
        for s in res.sources:
            summary.append(f"- {s.title} ({s.url})")
    return "\n".join(summary)

class DeepScribePipeline:
    """
    DeepScribe AI Pipeline.
    
    Orchestrates the full blog creation workflow using LangChain chains:
    1. Title Strategist
    2. Content Planner
    3. Research Agents (parallelized)
    4. Writer
    5. Editor (with Validator feedback)
    """

    def __init__(self):
        from app.core.llm import get_llm
        self.llm = get_llm(temperature=0.7)
        self.fast_llm = get_llm(temperature=0.3)  # Use lower temp/faster model for some tasks if needed
        
        # Initialize chains
        self.title_chain = create_title_chain(self.llm)
        self.planner_chain = create_planner_chain(self.llm)
        self.research_chain = create_researcher_chain(self.fast_llm)
        self.writer_chain = create_writer_chain(self.llm)

        self.insight_chain = create_insight_validator_chain(self.fast_llm)
        self.editor_chain = create_editor_chain(self.llm)

    async def run_full_pipeline(
        self,
        project_id: str,
        topic: str,
        target_audience: str,
        goal: str,
        tone: str,
        expertise_level: str,
        title: str,
        sections: List[dict],
        on_progress: callable = None,
    ) -> dict:
        """
        Run the full content creation pipeline.
        """
        logger.info("pipeline_started", project_id=project_id)
        
        try:
            # Phase 1: Research
            if on_progress:
                await on_progress("research", "Starting parallel research", 20)
            
            research_tasks = []
            for section in sections:
                task = invoke_with_retry(self.research_chain, {
                    "heading": section["heading"],
                    "key_points": section.get("key_points", []),
                    "topic": topic,
                    "target_audience": target_audience
                })
                research_tasks.append(task)
            
            # Run research in parallel
            research_results = await asyncio.gather(*research_tasks)
            
            # Map research to section headings
            research_map = {res.heading: res for res in research_results}
            
            # Phase 2: Writing
            if on_progress:
                await on_progress("writing", "Drafting content sections", 50)
            
            writing_tasks = []
            for section in sections:
                heading = section["heading"]
                section_research = research_map.get(heading)
                
                research_text = f"Sources: {section_research.sources}\nFacts: {section_research.key_facts}\nStats: {section_research.statistics}" if section_research else "No specific research found."
                
                
                # Optimize payload: Use compact source list
                compact_sources = summarize_sources_text(section_research.sources) if section_research else ""
                # Truncate research text if needed
                
                task = invoke_with_retry(self.writer_chain, {
                    "heading": heading,
                    "key_points": section.get("key_points", []),
                    "word_count": section.get("estimated_words", 300),
                    "tone": tone,
                    "expertise_level": expertise_level,
                    "research_content": research_text[:6000], # HARD TRUNCATE to safe limit (~1500 tokens)
                    "sources": compact_sources
                })
                writing_tasks.append(task)
            
            # Run writing in parallel (or sequential if rate limits are a concern)
            # Using gather for parallel writing which typically yields better performance
            written_sections = await asyncio.gather(*writing_tasks)
            
            # Aggregate full draft
            full_draft = "\n\n".join([sec.content for sec in written_sections])
            full_word_count = sum([sec.word_count for sec in written_sections])
            
            logger.info("writing_phase_complete", project_id=project_id, word_count=full_word_count)
            
            # Phase 3: Editing & Validation
            if on_progress:
                await on_progress("editing", "Validating and polishing content", 80)
            
            # Run Insight Validator
            insight_result = await invoke_with_retry(self.insight_chain, {
                "content": full_draft,
                "topic": topic,
                "target_audience": target_audience,
                "goal": goal
            })
            
            # Prepare feedback for editor
            editor_feedback = f"""
            INSIGHT Feedback:
            Primary Insight: {insight_result.primary_insight}
            Suggestions: {insight_result.suggestions}
            """
            
            # Final Edit
            # Optimize payload: Use compact summaries
            all_sources_compact = summarize_all_research(research_results)
            
            final_edit = await invoke_with_retry(self.editor_chain, {
                "content": full_draft[:12000], # Truncate draft if absolutely massive (~3000 tokens)
                "sources": all_sources_compact,
                "topic": topic,
                "target_audience": target_audience,
                "goal": goal,
                "tone": tone,
                "expertise_level": expertise_level,
            })
            
            logger.info("pipeline_completed", project_id=project_id, final_word_count=final_edit.word_count)
            
            if on_progress:
                await on_progress("complete", "Pipeline complete", 100)
            
            return {
                "content": final_edit.final_content,
                "research": str([res.dict() for res in research_results]),
                "insight_scores": insight_result.dict(),

                "word_count": final_edit.word_count
            }
            
        except Exception as e:
            logger.error("pipeline_failed", project_id=project_id, error=str(e))
            raise
