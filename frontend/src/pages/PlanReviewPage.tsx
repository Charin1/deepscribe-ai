import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
    FileText,
    GripVertical,
    Plus,
    Trash2,
    Lock,
    Unlock,
    BookOpen,
    Loader2,
    CheckCircle2,
    ArrowRight
} from 'lucide-react'
import { api } from '../services/api'
import { PlanSection } from '../types'

export default function PlanReviewPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: project, isLoading: projectLoading } = useQuery({
        queryKey: ['project', id],
        queryFn: () => api.getProject(id!),
    })

    const { data: plan, isLoading: planLoading } = useQuery({
        queryKey: ['plan', id],
        queryFn: () => api.getPlan(id!),
        enabled: !!id,
    })

    const [sections, setSections] = useState<PlanSection[]>([])

    const saveMutation = useMutation({
        mutationFn: async () => {
            // Transform sections to match API expectations
            const sectionsPayload = sections.map(s => ({
                heading: s.heading,
                heading_level: s.heading_level,
                key_points: s.key_points,
                estimated_words: s.estimated_words,
                is_locked: s.is_locked,
                parent_id: s.parent_id
            }))

            return api.updatePlan(id!, sectionsPayload)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['plan', id] })
        }
    })

    const approveMutation = useMutation({
        mutationFn: async () => {
            // Save first to ensure latest changes are used
            await saveMutation.mutateAsync()
            return api.approvePlan(id!)
        },
        onSuccess: async () => {
            // Start execution after approval
            await api.startExecution(id!)
            queryClient.invalidateQueries({ queryKey: ['project', id] })
            navigate(`/projects/${id}/execution`)
        },
    })

    // Initialize sections from plan data
    if (plan?.sections && sections.length === 0) {
        setSections(plan.sections)
    }

    const isLoading = projectLoading || planLoading

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
        )
    }

    const totalWords = sections.reduce((sum, s) => sum + s.estimated_words, 0)

    const toggleLock = (sectionId: string) => {
        setSections(sections.map(s =>
            s.id === sectionId ? { ...s, is_locked: !s.is_locked } : s
        ))
    }

    const updateSection = (sectionId: string, updates: Partial<PlanSection>) => {
        setSections(sections.map(s =>
            s.id === sectionId ? { ...s, ...updates } : s
        ))
    }

    const removeSection = (sectionId: string) => {
        setSections(sections.filter(s => s.id !== sectionId))
    }

    const addSection = () => {
        const newSection: PlanSection = {
            id: `new-${Date.now()}`,
            heading: 'New Section',
            heading_level: 2,
            key_points: [],
            suggested_sources: [],
            estimated_words: 300,
            order: sections.length,
            is_locked: false,
            parent_id: null,
        }
        setSections([...sections, newSection])
    }

    return (
        <div className="space-y-8">
            <button
                onClick={() => navigate(`/projects/${id}/titles`)}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Titles
            </button>

            {/* Header */}
            <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>Step 2 of 5</span>
                    <span>•</span>
                    <span>Plan Review</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Review Your Outline</h1>
                <p className="text-gray-600">
                    Edit the structure and approve when ready
                </p>
            </div>

            {/* Progress Bar */}
            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full w-[40%] bg-primary-600 transition-all" />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="card text-center bg-white border-gray-200">
                    <div className="text-3xl font-bold text-gray-900">{sections.length}</div>
                    <div className="text-sm text-gray-500">Sections</div>
                </div>
                <div className="card text-center bg-white border-gray-200">
                    <div className="text-3xl font-bold text-primary-600">{totalWords.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">Est. Words</div>
                </div>
                <div className="card text-center bg-white border-gray-200">
                    <div className="text-3xl font-bold text-red-500">
                        {sections.filter(s => s.is_locked).length}
                    </div>
                    <div className="text-sm text-gray-500">Locked</div>
                </div>
            </div>

            {/* Sections */}
            <div className="space-y-4">
                {sections.map((section, index) => (
                    <div
                        key={section.id}
                        className={`
              card transition-all bg-white border-gray-200
              ${section.is_locked ? 'border-red-200 bg-red-50' : 'hover:border-primary-300'}
            `}
                    >
                        <div className="flex items-start gap-4">
                            {/* Drag Handle */}
                            <div className="cursor-grab text-gray-400 hover:text-gray-600 pt-1">
                                <GripVertical className="w-5 h-5" />
                            </div>

                            {/* Content */}
                            <div className="flex-1 space-y-4">
                                {/* Header Row */}
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-gray-500 font-mono">
                                        H{section.heading_level}
                                    </span>
                                    <input
                                        type="text"
                                        value={section.heading}
                                        onChange={(e) => updateSection(section.id, { heading: e.target.value })}
                                        disabled={section.is_locked}
                                        className="flex-1 bg-transparent text-lg font-semibold text-gray-900 border-none focus:outline-none focus:ring-0 disabled:opacity-60"
                                    />
                                    <span className="text-sm text-gray-500">
                                        ~{section.estimated_words} words
                                    </span>
                                </div>

                                {/* Key Points */}
                                <div className="pl-4 border-l-2 border-gray-200">
                                    <div className="text-sm text-gray-500 mb-2">Key points:</div>
                                    <ul className="space-y-1">
                                        {section.key_points.map((point, i) => (
                                            <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                                                <span className="w-1.5 h-1.5 bg-primary-400 rounded-full" />
                                                {point}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Word Count Slider */}
                                {!section.is_locked && (
                                    <div className="flex items-center gap-4">
                                        <span className="text-sm text-gray-500">Words:</span>
                                        <input
                                            type="range"
                                            min={100}
                                            max={1000}
                                            step={50}
                                            value={section.estimated_words}
                                            onChange={(e) => updateSection(section.id, {
                                                estimated_words: parseInt(e.target.value)
                                            })}
                                            className="flex-1 accent-primary-600"
                                        />
                                        <span className="text-sm text-gray-900 w-16 text-right">
                                            {section.estimated_words}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => toggleLock(section.id)}
                                    className={`
                    p-2 rounded-lg transition-colors
                    ${section.is_locked
                                            ? 'bg-red-100 text-red-600'
                                            : 'bg-gray-100 text-gray-500 hover:text-gray-700'}
                  `}
                                    title={section.is_locked ? 'Unlock section' : 'Lock section'}
                                >
                                    {section.is_locked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                                </button>

                                {!section.is_locked && (
                                    <button
                                        onClick={() => removeSection(section.id)}
                                        className="p-2 rounded-lg bg-gray-100 text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                                        title="Remove section"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Add Section Button */}
                <button
                    onClick={addSection}
                    className="w-full py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-500 hover:text-primary-600 hover:border-primary-400 hover:bg-primary-50 transition-all flex items-center justify-center gap-2"
                >
                    <Plus className="w-5 h-5" />
                    Add Section
                </button>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-500">
                    <BookOpen className="w-4 h-4 inline mr-1" />
                    {totalWords.toLocaleString()} words in {sections.length} sections
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => saveMutation.mutate()}
                        disabled={saveMutation.isPending || approveMutation.isPending}
                        className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
                    >
                        {saveMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                        {saveMutation.isPending ? 'Saving...' : 'Save Draft'}
                    </button>

                    <button
                        onClick={() => approveMutation.mutate()}
                        disabled={approveMutation.isPending}
                        className="btn-primary flex items-center gap-2"
                    >
                        {approveMutation.isPending ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Starting Research...
                            </>
                        ) : (
                            <>
                                <CheckCircle2 className="w-5 h-5" />
                                Approve & Start Research
                                <ArrowRight className="w-5 h-5" />
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
