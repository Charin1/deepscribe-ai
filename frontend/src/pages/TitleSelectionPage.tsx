import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
    Lightbulb,
    Target,
    BarChart2,
    CheckCircle2,
    Loader2,
    ArrowRight
} from 'lucide-react'
import { api } from '../services/api'
import { Title } from '../types'

const difficultyColors = [
    'bg-green-500', 'bg-green-500', 'bg-green-400', 'bg-yellow-400',
    'bg-yellow-500', 'bg-orange-400', 'bg-orange-500', 'bg-red-400',
    'bg-red-500', 'bg-red-600'
]

const intentLabels: Record<string, { label: string; color: string }> = {
    informational: { label: 'Informational', color: 'bg-blue-500/20 text-blue-400' },
    navigational: { label: 'Navigational', color: 'bg-purple-500/20 text-purple-400' },
    transactional: { label: 'Transactional', color: 'bg-green-500/20 text-green-400' },
    commercial: { label: 'Commercial', color: 'bg-yellow-500/20 text-yellow-400' },
}

export default function TitleSelectionPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: project, isLoading } = useQuery({
        queryKey: ['project', id],
        queryFn: () => api.getProject(id!),
    })

    const { data: titlesData } = useQuery({
        queryKey: ['titles', id],
        queryFn: () => api.getTitles(id!),
        enabled: !!id,
    })

    const selectMutation = useMutation({
        mutationFn: (titleId: string) => api.selectTitle(id!, titleId),
        onSuccess: async () => {
            // Generate plan after title selection
            await api.generatePlan(id!)
            queryClient.invalidateQueries({ queryKey: ['project', id] })
            navigate(`/projects/${id}/plan`)
        },
    })

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
        )
    }

    const titles = titlesData?.titles || []

    return (
        <div className="space-y-8">
            <button
                onClick={() => navigate('/projects')}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Projects
            </button>

            {/* Header */}
            <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>Step 1 of 5</span>
                    <span>•</span>
                    <span>Title Selection</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Choose Your Title</h1>
                <p className="text-gray-600">
                    Select the title that best fits your content goals for: <span className="text-gray-900 font-medium">{project?.topic}</span>
                </p>
            </div>

            {/* Progress Bar */}
            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full w-[20%] bg-primary-600 transition-all" />
            </div>

            {/* Titles Grid */}
            <div className="space-y-4">
                {titles.map((title: Title, index: number) => {
                    const intent = intentLabels[title.search_intent] || intentLabels.informational
                    const isSelected = title.is_selected

                    return (
                        <button
                            key={title.id}
                            onClick={() => !selectMutation.isPending && selectMutation.mutate(title.id)}
                            disabled={selectMutation.isPending}
                            className={`
                w-full text-left p-6 rounded-2xl border transition-all duration-300
                ${isSelected
                                    ? 'bg-red-50 border-primary-500 ring-1 ring-primary-500'
                                    : 'bg-white border-gray-200 hover:border-primary-300 hover:shadow-md'}
                ${selectMutation.isPending ? 'opacity-50 cursor-wait' : 'cursor-pointer'}
              `}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 space-y-3">
                                    {/* Title Number */}
                                    <div className="flex items-center gap-3">
                                        <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium ${isSelected ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-500'}`}>
                                            {index + 1}
                                        </span>
                                        {isSelected && (
                                            <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded-full flex items-center gap-1">
                                                <CheckCircle2 className="w-3 h-3" />
                                                Selected
                                            </span>
                                        )}
                                    </div>

                                    {/* Title Text */}
                                    <h3 className={`text-xl font-semibold ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                                        {title.title}
                                    </h3>

                                    {/* Description */}
                                    <p className="text-gray-600">
                                        {title.description}
                                    </p>

                                    {/* Meta */}
                                    <div className="flex items-center gap-4 pt-2">
                                        {/* Search Intent */}
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${intent.color}`}>
                                            <Target className="w-3 h-3 inline mr-1" />
                                            {intent.label}
                                        </span>

                                        {/* Difficulty */}
                                        <span className="flex items-center gap-2 text-sm text-gray-500">
                                            <BarChart2 className="w-4 h-4" />
                                            Difficulty:
                                            <span className="flex gap-0.5">
                                                {[...Array(10)].map((_, i) => (
                                                    <span
                                                        key={i}
                                                        className={`w-2 h-2 rounded-full ${i < title.difficulty
                                                            ? difficultyColors[title.difficulty - 1]
                                                            : 'bg-gray-200'
                                                            }`}
                                                    />
                                                ))}
                                            </span>
                                        </span>
                                    </div>
                                </div>

                                {/* Selection Indicator */}
                                <div className={`
                  w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all
                  ${isSelected
                                        ? 'bg-primary-600 border-primary-600'
                                        : 'border-gray-300 hover:border-primary-400'}
                `}>
                                    {isSelected && <CheckCircle2 className="w-4 h-4 text-white" />}
                                </div>
                            </div>
                        </button>
                    )
                })}
            </div>

            {/* Loading State */}
            {selectMutation.isPending && (
                <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
                    <div className="card text-center p-8 bg-white shadow-xl border border-gray-200">
                        <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Generating Content Plan</h3>
                        <p className="text-gray-600">Please wait while our AI creates your outline...</p>
                    </div>
                </div>
            )}

            {/* Help Text */}
            <div className="card bg-blue-50 border-blue-100">
                <div className="flex items-start gap-4">
                    <Lightbulb className="w-6 h-6 text-blue-500 flex-shrink-0" />
                    <div>
                        <h3 className="font-medium text-blue-900 mb-1">Tips for choosing a title</h3>
                        <ul className="text-sm text-blue-700 space-y-1">
                            <li>• Consider your SEO goals and target keywords</li>
                            <li>• Lower difficulty means less competition</li>
                            <li>• Match the search intent to your content goals</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    )
}
