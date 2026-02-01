import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Download, Copy, CheckCircle2, FileText, Code, Globe, Loader2, ArrowRight } from 'lucide-react'
import { api } from '../services/api'

export default function ExportPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [format, setFormat] = useState<'markdown' | 'html' | 'wordpress'>('markdown')
    const [copied, setCopied] = useState(false)

    const { data: draft } = useQuery({ queryKey: ['draft', id], queryFn: () => api.getDraft(id!) })

    const exportMutation = useMutation({
        mutationFn: () => api.exportDraft(id!, format),
    })

    const handleCopy = async () => {
        if (exportMutation.data?.content) {
            await navigator.clipboard.writeText(exportMutation.data.content)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        }
    }

    const handleDownload = () => {
        if (exportMutation.data?.content) {
            const ext = format === 'markdown' ? 'md' : 'html'
            const blob = new Blob([exportMutation.data.content], { type: 'text/plain' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url; a.download = `article.${ext}`; a.click()
            URL.revokeObjectURL(url)
        }
    }

    const formats = [
        { value: 'markdown', label: 'Markdown', icon: FileText },
        { value: 'html', label: 'HTML', icon: Code },
        { value: 'wordpress', label: 'WordPress', icon: Globe },
    ] as const

    return (
        <div className="space-y-8">
            <button
                onClick={() => navigate(`/projects/${id}/draft`)}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Draft
            </button>

            <div>
                <div className="text-sm text-gray-500">Step 5 of 5 • Export</div>
                <h1 className="text-3xl font-bold text-gray-900">Export Your Content</h1>
            </div>

            <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full w-full bg-primary-600" />
            </div>

            <div className="card bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Format</h3>
                <div className="grid grid-cols-3 gap-4">
                    {formats.map(f => (
                        <button key={f.value} onClick={() => { setFormat(f.value); exportMutation.mutate() }}
                            className={`p-4 rounded-xl border text-center transition-all ${format === f.value ? 'bg-red-50 border-primary-500 ring-1 ring-primary-500 text-primary-700' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'}`}>
                            <f.icon className={`w-8 h-8 mx-auto mb-2 ${format === f.value ? 'text-primary-600' : 'text-gray-400'}`} />
                            {f.label}
                        </button>
                    ))}
                </div>
            </div>

            {draft?.seo_title && (
                <div className="card bg-white border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">SEO Metadata</h3>
                    <div className="space-y-3">
                        <div>
                            <div className="text-sm text-gray-500">Title</div>
                            <div className="text-gray-900 font-medium">{draft.seo_title}</div>
                        </div>
                        <div>
                            <div className="text-sm text-gray-500">Description</div>
                            <div className="text-gray-900">{draft.meta_description}</div>
                        </div>
                    </div>
                </div>
            )}

            {exportMutation.isPending && <div className="text-center py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" /></div>}

            {exportMutation.data && (
                <div className="card bg-white border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Preview</h3>
                        <div className="flex gap-2">
                            <button onClick={handleCopy} className="btn-secondary flex items-center gap-2">{copied ? <CheckCircle2 className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}{copied ? 'Copied!' : 'Copy'}</button>
                            <button onClick={handleDownload} className="btn-primary flex items-center gap-2"><Download className="w-4 h-4" />Download</button>
                        </div>
                    </div>
                    <pre className="bg-gray-900 p-4 rounded-lg overflow-auto max-h-96 text-sm text-gray-300 font-mono">{exportMutation.data.content}</pre>
                </div>
            )}

            <div className="card bg-green-50 border-green-200 text-center py-8">
                <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-green-800 mb-2">Content Complete!</h2>
                <p className="text-green-700">Your AI-generated blog post is ready for publication.</p>
            </div>
        </div>
    )
}
