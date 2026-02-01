import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
    Plus,
    FileText,
    Clock,
    CheckCircle2,
    AlertCircle,
    ChevronRight,
    Loader2
} from 'lucide-react'
import { api } from '../services/api'
import { Project, ProjectStatus } from '../types'

const statusConfig: Record<ProjectStatus, { label: string; color: string; icon: React.ElementType }> = {
    created: { label: 'Draft', color: 'text-gray-400', icon: FileText },
    titles_generated: { label: 'Titles Ready', color: 'text-blue-400', icon: Clock },
    title_selected: { label: 'Title Selected', color: 'text-blue-400', icon: CheckCircle2 },
    plan_generated: { label: 'Plan Ready', color: 'text-yellow-400', icon: Clock },
    plan_approved: { label: 'Plan Approved', color: 'text-yellow-400', icon: CheckCircle2 },
    researching: { label: 'Researching', color: 'text-primary-400', icon: Loader2 },
    writing: { label: 'Writing', color: 'text-primary-400', icon: Loader2 },
    editing: { label: 'Editing', color: 'text-primary-400', icon: Loader2 },
    draft_ready: { label: 'Draft Ready', color: 'text-accent-400', icon: CheckCircle2 },
    published: { label: 'Published', color: 'text-green-400', icon: CheckCircle2 },
    failed: { label: 'Failed', color: 'text-red-400', icon: AlertCircle },
}

function getNextStep(status: ProjectStatus): { href: string; label: string } {
    switch (status) {
        case 'created':
        case 'titles_generated':
            return { href: 'titles', label: 'Select Title' }
        case 'title_selected':
        case 'plan_generated':
            return { href: 'plan', label: 'Review Plan' }
        case 'plan_approved':
        case 'researching':
        case 'writing':
        case 'editing':
            return { href: 'execution', label: 'View Progress' }
        case 'draft_ready':
            return { href: 'draft', label: 'Review Draft' }
        case 'published':
            return { href: 'export', label: 'View Export' }
        default:
            return { href: '', label: 'View' }
    }
}

export default function ProjectsPage() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['projects'],
        queryFn: () => api.getProjects(),
    })

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="card bg-red-500/10 border-red-500/30 text-center py-12">
                <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">Failed to load projects</h2>
                <p className="text-gray-400">Please try again later.</p>
            </div>
        )
    }

    const projects = data?.items || []

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
                    <p className="text-gray-600 mt-1">Manage your content creation projects</p>
                </div>
                <Link to="/projects/new" className="btn-primary flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    New Project
                </Link>
            </div>

            {/* Projects Grid */}
            {projects.length === 0 ? (
                <div className="card text-center py-16 bg-white border-gray-200">
                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">No projects yet</h2>
                    <p className="text-gray-500 mb-6">Create your first AI-powered blog post</p>
                    <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
                        <Plus className="w-5 h-5" />
                        Create Project
                    </Link>
                </div>
            ) : (
                <div className="grid gap-4">
                    {projects.map((project: Project) => {
                        const status = statusConfig[project.status]
                        const nextStep = getNextStep(project.status)
                        const StatusIcon = status.icon

                        return (
                            <Link
                                key={project.id}
                                to={`/projects/${project.id}/${nextStep.href}`}
                                className="card-interactive flex items-center justify-between group bg-white border-gray-200 hover:border-primary-200 hover:bg-gray-50"
                            >
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                                        {project.topic}
                                    </h3>
                                    <p className="text-gray-500 text-sm mb-3 line-clamp-1">
                                        {project.target_audience} • {project.goal}
                                    </p>
                                    <div className="flex items-center gap-4 text-sm">
                                        <span className={`flex items-center gap-1.5 font-medium ${status.color.replace('400', '600')}`}>
                                            <StatusIcon className={`w-4 h-4 ${project.status.includes('ing') ? 'animate-spin' : ''}`} />
                                            {status.label}
                                        </span>
                                        <span className="text-gray-400">
                                            {new Date(project.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                                        {nextStep.label}
                                    </span>
                                    <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />

                                    <button
                                        onClick={(e) => {
                                            e.preventDefault(); // Prevent navigation
                                            if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
                                                api.deleteProject(project.id).then(() => {
                                                    // Refresh list (using window.location for simplicity, or refetch query)
                                                    window.location.reload();
                                                }).catch(() => alert('Failed to delete project'));
                                            }
                                        }}
                                        className="p-2 text-gray-400 hover:text-red-500 transition-colors z-10"
                                        title="Delete Project"
                                    >
                                        <div className="w-4 h-4">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /></svg>
                                        </div>
                                    </button>
                                </div>
                            </Link>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
