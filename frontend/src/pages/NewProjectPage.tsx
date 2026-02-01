import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
    Sparkles,
    Users,
    Target,
    MessageSquare,
    GraduationCap,
    FileText,
    Loader2,
    ArrowRight
} from 'lucide-react'
import { api } from '../services/api'

type Goal = 'seo' | 'thought_leadership' | 'technical' | 'marketing'
type Tone = 'authoritative' | 'conversational' | 'academic' | 'persuasive'
type ExpertiseLevel = 'beginner' | 'intermediate' | 'expert'

const goals: { value: Goal; label: string; description: string }[] = [
    { value: 'seo', label: 'SEO', description: 'Optimize for search engine rankings' },
    { value: 'thought_leadership', label: 'Thought Leadership', description: 'Establish industry authority' },
    { value: 'technical', label: 'Technical', description: 'Deep technical documentation' },
    { value: 'marketing', label: 'Marketing', description: 'Drive conversions and engagement' },
]

const tones: { value: Tone; label: string }[] = [
    { value: 'authoritative', label: 'Authoritative' },
    { value: 'conversational', label: 'Conversational' },
    { value: 'academic', label: 'Academic' },
    { value: 'persuasive', label: 'Persuasive' },
]

const expertiseLevels: { value: ExpertiseLevel; label: string; description: string }[] = [
    { value: 'beginner', label: 'Beginner', description: 'New to the topic' },
    { value: 'intermediate', label: 'Intermediate', description: 'Familiar with basics' },
    { value: 'expert', label: 'Expert', description: 'Deep knowledge expected' },
]

export default function NewProjectPage() {
    const navigate = useNavigate()

    const [formData, setFormData] = useState({
        topic: '',
        target_audience: '',
        goal: 'seo' as Goal,
        tone: 'authoritative' as Tone,
        expertise_level: 'intermediate' as ExpertiseLevel,
        word_count_min: 1500,
        word_count_max: 3000,
        constraints: '',
    })

    const createMutation = useMutation({
        mutationFn: api.createProject,
        onSuccess: async (project) => {
            // Generate titles immediately
            await api.generateTitles(project.id)
            navigate(`/projects/${project.id}/titles`)
        },
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        createMutation.mutate(formData)
    }

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            <button
                onClick={() => navigate('/projects')}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Projects
            </button>

            {/* Header */}
            <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-primary-500/20">
                    <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900">Create New Project</h1>
                <p className="text-gray-600">Define your topic and let AI handle the rest</p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Topic */}
                <div className="card bg-white border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-primary-600" />
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900">Topic & Audience</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Topic *
                            </label>
                            <input
                                type="text"
                                value={formData.topic}
                                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                                placeholder="e.g., Machine Learning for Beginners"
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:bg-white"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                <Users className="w-4 h-4 inline mr-1 text-gray-400" />
                                Target Audience *
                            </label>
                            <input
                                type="text"
                                value={formData.target_audience}
                                onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                                placeholder="e.g., Software developers new to ML"
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:bg-white"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Goal */}
                <div className="card bg-white border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <Target className="w-5 h-5 text-primary-600" />
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900">Content Goal</h2>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        {goals.map((goal) => (
                            <button
                                key={goal.value}
                                type="button"
                                onClick={() => setFormData({ ...formData, goal: goal.value })}
                                className={`
                  p-4 rounded-xl border text-left transition-all duration-300
                  ${formData.goal === goal.value
                                        ? 'bg-red-50 border-primary-500 ring-1 ring-primary-500'
                                        : 'bg-white border-gray-200 hover:border-primary-200 hover:shadow-md'}
                `}
                            >
                                <div className={`font-medium ${formData.goal === goal.value ? 'text-primary-700' : 'text-gray-900'}`}>{goal.label}</div>
                                <div className={`text-sm mt-1 ${formData.goal === goal.value ? 'text-primary-600' : 'text-gray-500'}`}>{goal.description}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Tone & Expertise */}
                <div className="card bg-white border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                            <MessageSquare className="w-5 h-5 text-primary-600" />
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900">Tone & Style</h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Writing Tone
                            </label>
                            <select
                                value={formData.tone}
                                onChange={(e) => setFormData({ ...formData, tone: e.target.value as Tone })}
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 focus:bg-white"
                            >
                                {tones.map((tone) => (
                                    <option key={tone.value} value={tone.value}>
                                        {tone.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                <GraduationCap className="w-4 h-4 inline mr-1 text-gray-400" />
                                Expertise Level
                            </label>
                            <select
                                value={formData.expertise_level}
                                onChange={(e) => setFormData({ ...formData, expertise_level: e.target.value as ExpertiseLevel })}
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 focus:bg-white"
                            >
                                {expertiseLevels.map((level) => (
                                    <option key={level.value} value={level.value}>
                                        {level.label} - {level.description}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Word Count */}
                <div className="card bg-white border-gray-200 shadow-sm">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Word Count Range</h2>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Minimum
                            </label>
                            <input
                                type="number"
                                value={formData.word_count_min}
                                onChange={(e) => setFormData({ ...formData, word_count_min: parseInt(e.target.value) })}
                                min={500}
                                max={10000}
                                step={100}
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 focus:bg-white"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Maximum
                            </label>
                            <input
                                type="number"
                                value={formData.word_count_max}
                                onChange={(e) => setFormData({ ...formData, word_count_max: parseInt(e.target.value) })}
                                min={500}
                                max={20000}
                                step={100}
                                className="input-field bg-gray-50 border-gray-200 text-gray-900 focus:bg-white"
                            />
                        </div>
                    </div>
                </div>

                {/* Constraints (Optional) */}
                <div className="card bg-white border-gray-200 shadow-sm">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Constraints (Optional)</h2>
                    <textarea
                        value={formData.constraints}
                        onChange={(e) => setFormData({ ...formData, constraints: e.target.value })}
                        placeholder="e.g., Focus on Python examples, include code snippets, avoid jargon..."
                        rows={3}
                        className="input-field bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:bg-white resize-none"
                    />
                </div>

                {/* Submit */}
                <button
                    type="submit"
                    disabled={createMutation.isPending || !formData.topic || !formData.target_audience}
                    className="btn-primary w-full flex items-center justify-center gap-2 py-4 text-lg shadow-lg shadow-primary-500/20"
                >
                    {createMutation.isPending ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Creating Project...
                        </>
                    ) : (
                        <>
                            Generate Titles
                            <ArrowRight className="w-5 h-5" />
                        </>
                    )}
                </button>

                {createMutation.isError && (
                    <div className="text-center text-red-600 text-sm bg-red-50 p-2 rounded-lg">
                        Failed to create project. Please try again.
                    </div>
                )}
            </form>
        </div>
    )
}
