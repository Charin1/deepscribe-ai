import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Edit3, CheckCircle2, Loader2, ArrowRight, Shield } from 'lucide-react'
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

    const eeat = draft?.eeat_score

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

            {eeat && (
                <div className="card bg-white border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Shield className="w-5 h-5 mr-2 text-primary-600" />
                        E-E-A-T Score
                    </h3>
                    <div className="grid grid-cols-4 gap-4">
                        {[{ l: 'Experience', v: eeat.experience_score }, { l: 'Expertise', v: eeat.expertise_score }, { l: 'Authority', v: eeat.authority_score }, { l: 'Trust', v: eeat.trust_score }].map(s => (
                            <div key={s.l} className="text-center">
                                <div className="text-2xl font-bold text-primary-600">{s.v}</div>
                                <div className="text-sm text-gray-500">{s.l}</div>
                            </div>
                        ))}
                    </div>
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
