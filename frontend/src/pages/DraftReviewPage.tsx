import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Edit3, CheckCircle2, Loader2, ArrowRight, Lightbulb } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../services/api'

export default function DraftReviewPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()

    const { data: draft, isLoading } = useQuery({
        queryKey: ['draft', id],
        queryFn: () => api.getDraft(id!),
    })

    const approveMutation = useMutation({
        mutationFn: () => api.approveDraft(id!),
        onSuccess: () => navigate(`/projects/${id}/export`),
    })

    if (isLoading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 text-primary-400 animate-spin" /></div>

    return (
        <div className="space-y-8">
            <button
                onClick={() => navigate(`/projects/${id}/execution`)}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Execution
            </button>

            <div>
                <div className="text-sm text-gray-500">Step 4 of 5 • Draft Review</div>
                <h1 className="text-3xl font-bold text-gray-900">Review Your Draft</h1>
            </div>

            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full w-[80%] bg-primary-600" />
            </div>

            {draft?.insight_score && (
                <div className="card bg-white border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Lightbulb className="w-5 h-5 mr-2 text-primary-600" />
                        I-N-S-I-G-H-T Score
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        {[
                            { l: 'Inspiring', v: draft.insight_score.inspiring_score },
                            { l: 'Novel', v: draft.insight_score.novel_score },
                            { l: 'Structured', v: draft.insight_score.structured_score },
                            { l: 'Informative', v: draft.insight_score.informative_score },
                            { l: 'Grounded', v: draft.insight_score.grounded_score },
                            { l: 'Helpful', v: draft.insight_score.helpful_score },
                            { l: 'Trustworthy', v: draft.insight_score.trustworthy_score },
                            { l: 'Overall', v: draft.insight_score.overall_score }
                        ].map(s => (
                            <div key={s.l} className="text-center p-3 bg-gray-50 rounded-lg">
                                <div className="text-2xl font-bold text-primary-600">{Math.round(s.v)}</div>
                                <div className="text-xs text-gray-500 uppercase tracking-wide mt-1">{s.l}</div>
                            </div>
                        ))}
                    </div>

                    {draft.insight_score.primary_insight && (
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 mb-4">
                            <h4 className="text-sm font-semibold text-blue-900 mb-1">Testing Primary Insight</h4>
                            <p className="text-blue-800 text-sm">{draft.insight_score.primary_insight}</p>
                        </div>
                    )}
                </div>
            )}

            <div className="card bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Edit3 className="w-5 h-5 mr-2 text-primary-600" />
                    Content
                </h3>
                <div className="prose max-w-none text-gray-800">
                    <ReactMarkdown>{draft?.content_markdown || ''}</ReactMarkdown>
                </div>
            </div>

            <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-500">{draft?.word_count?.toLocaleString()} words</div>
                <button onClick={() => approveMutation.mutate()} disabled={approveMutation.isPending} className="btn-primary flex items-center gap-2">
                    {approveMutation.isPending ? <><Loader2 className="w-5 h-5 animate-spin" />Approving...</> : <><CheckCircle2 className="w-5 h-5" />Approve & Export<ArrowRight className="w-5 h-5" /></>}
                </button>
            </div>
        </div>
    )
}
