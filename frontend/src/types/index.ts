// API Types

export type ProjectStatus =
    | 'created' | 'titles_generated' | 'title_selected'
    | 'plan_generated' | 'plan_approved' | 'researching'
    | 'writing' | 'editing' | 'draft_ready' | 'published' | 'failed'

export interface Project {
    id: string
    topic: string
    target_audience: string
    goal: string
    tone: string
    expertise_level: string
    word_count_min: number
    word_count_max: number
    constraints?: string
    status: ProjectStatus
    selected_title_id?: string
    created_at: string
    updated_at: string
}

export interface Title {
    id: string
    title: string
    description: string
    search_intent: string
    difficulty: number
    is_selected: boolean
    created_at: string
}

export interface PlanSection {
    id: string
    heading: string
    heading_level: number
    key_points: string[]
    suggested_sources: string[]
    estimated_words: number
    order: number
    is_locked: boolean
    parent_id: string | null
}

export interface Plan {
    id: string
    project_id: string
    is_approved: boolean
    total_estimated_words: number
    sections: PlanSection[]
    created_at: string
    updated_at: string
}

export interface EEATScore {
    experience_score: number
    expertise_score: number
    authority_score: number
    trust_score: number
    overall_score: number
    experience_feedback?: string
    expertise_feedback?: string
    authority_feedback?: string
    trust_feedback?: string
    weak_sections: string[]
}

export interface Draft {
    id: string
    project_id: string
    content_markdown: string
    content_html?: string
    word_count: number
    version: number
    is_current: boolean
    is_approved: boolean
    seo_title?: string
    meta_description?: string
    faq_schema?: object[]
    eeat_score?: EEATScore
    created_at: string
    updated_at: string
}

export interface AgentLogEntry {
    timestamp: string
    agent: string
    message: string
    level?: string
}

export interface ExecutionStatus {
    project_id: string
    status: ProjectStatus
    current_agent?: string
    progress_percent: number
    logs: AgentLogEntry[]
    sources_discovered: number
    confidence_scores: Record<string, number>
}
