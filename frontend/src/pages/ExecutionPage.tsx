import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, PenTool, Edit3, CheckCircle2, Loader2, Clock, FileText, Link as LinkIcon, ArrowRight, RotateCcw } from 'lucide-react'
import { api } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'

interface AgentLog { timestamp: string; agent: string; message: string; level?: string }

export default function ExecutionPage() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [wsLogs, setWsLogs] = useState<AgentLog[]>([])

    const { data: status } = useQuery({
        queryKey: ['execution-status', id],
        queryFn: () => api.getExecutionStatus(id!),
        refetchInterval: 1000, // Faster polling to see progress
    })

    const restartMutation = useMutation({
        mutationFn: () => api.restartExecution(id!),
        onSuccess: () => {
            setWsLogs([]) // Clear local logs
            queryClient.invalidateQueries({ queryKey: ['execution-status', id] })
        },
    })

    const { lastMessage } = useWebSocket(id!)

    useEffect(() => {
        if (lastMessage?.type === 'agent_update' && lastMessage.agent && lastMessage.message) {
            setWsLogs(prev => [...prev, {
                timestamp: new Date().toISOString(),
                agent: lastMessage.agent as string,
                message: lastMessage.message as string,
                level: lastMessage.status as string || 'info'
            }])
        }
    }, [lastMessage])

    // Combine logs from API and WebSocket
    const logs = status?.logs?.length ? status.logs : wsLogs
    const progress = status?.progress_percent || 0
    const currentAgent = status?.current_agent
    const sourcesCount = status?.sources_discovered || 0

    // Auto-redirect removed to prevent navigation loops when using back button
    // User can manually click "View Draft" when ready

    const steps = [
        { key: 'researching', label: 'Research', icon: Search },
        { key: 'writing', label: 'Writing', icon: PenTool },
        { key: 'editing', label: 'Editing', icon: Edit3 },
        { key: 'draft_ready', label: 'Complete', icon: CheckCircle2 },
    ]
    const currentIdx = steps.findIndex(s => s.key === status?.status)

    return (
        <div className="space-y-8">
            <button
                onClick={() => navigate(`/projects/${id}/plan`)}
                className="flex items-center gap-2 text-gray-500 hover:text-primary-600 transition-colors"
            >
                <ArrowRight className="w-4 h-4 rotate-180" />
                Back to Plan
            </button>

            <div className="flex items-center justify-between">
                <div>
                    <div className="text-sm text-gray-500">Step 3 of 5 • AI Execution</div>
                    <h1 className="text-3xl font-bold text-gray-900">AI Agents at Work</h1>
                </div>
                <button
                    onClick={() => restartMutation.mutate()}
                    disabled={restartMutation.isPending}
                    className="btn-secondary flex items-center gap-2"
                >
                    <RotateCcw className={`w-4 h-4 ${restartMutation.isPending ? 'animate-spin' : ''}`} />
                    {restartMutation.isPending ? 'Restarting...' : 'Restart Execution'}
                </button>
            </div>

            <div className="card bg-white border-gray-200">
                <div className="flex items-center justify-between mb-6">
                    {steps.map((step, i) => {
                        const active = i === currentIdx, done = i < currentIdx
                        return (<div key={step.key} className="flex items-center">
                            <div className={`flex items-center gap-3 px-4 py-2 rounded-xl transition-all duration-300 ${active ? 'bg-red-50 border border-primary-500/50 text-primary-600 shadow-sm' : done ? 'text-green-600' : 'text-gray-400'}`}>
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${done ? 'bg-green-100' : active ? 'bg-red-100' : 'bg-gray-100'}`}>
                                    {active ? <Loader2 className="w-5 h-5 animate-spin text-primary-600" /> : done ? <CheckCircle2 className="w-5 h-5 text-green-600" /> : <step.icon className="w-5 h-5" />}
                                </div>
                                <span className="font-medium hidden sm:block">{step.label}</span>
                            </div>
                            {i < steps.length - 1 && <div className={`w-8 h-0.5 mx-2 ${i < currentIdx ? 'bg-green-500' : 'bg-gray-200'}`} />}
                        </div>)
                    })}
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-primary-600 transition-all duration-500" style={{ width: `${progress}%` }} />
                </div>
                <div className="text-right text-sm text-gray-500 mt-2">{progress.toFixed(0)}% complete</div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <div className="card bg-white border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Clock className="w-5 h-5 mr-2 text-primary-600" />
                        Current Agent
                    </h3>
                    {status?.status === 'draft_ready' ? (
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
                                <CheckCircle2 className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <div className="font-semibold text-gray-900">Execution Complete</div>
                                <div className="text-sm text-gray-500">Draft ready for review</div>
                            </div>
                        </div>
                    ) : currentAgent ? (
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center">
                                <Search className="w-6 h-6 text-primary-600" />
                            </div>
                            <div>
                                <div className="font-semibold text-gray-900">{currentAgent}</div>
                                <div className="text-sm text-gray-500 flex items-center">
                                    <Loader2 className="w-3 h-3 animate-spin mr-1" />
                                    Processing...
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-400">Initializing...</div>
                    )}
                </div>

                <div className="card bg-white border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <LinkIcon className="w-5 h-5 mr-2 text-primary-600" />
                        Sources Discovered
                    </h3>
                    <div className="text-4xl font-bold text-primary-600">{sourcesCount}</div>
                </div>
            </div>

            <div className="card bg-white border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-primary-600" />
                    Execution Log
                </h3>
                <div className="space-y-1 max-h-80 overflow-auto font-mono text-xs bg-gray-50 p-4 rounded-xl border border-gray-200">
                    {logs.length === 0 ? (
                        <div className="text-gray-500 text-center py-8">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-primary-400" />
                            Click "Restart Execution" to see live progress logs
                        </div>
                    ) : logs.map((l, i) => (
                        <div key={i} className={`p-2 rounded ${l.agent === 'HTTP' ? 'bg-blue-50 border border-blue-100' : 'bg-white border border-gray-100 shadow-sm'}`}>
                            <span className={`font-semibold ${l.agent === 'HTTP' ? 'text-blue-600' : l.agent === 'System' ? 'text-purple-600' : 'text-primary-600'}`}>{l.agent}</span>
                            <span className="text-gray-400 mx-2">→</span>
                            <span className={l.level === 'success' ? 'text-green-600' : l.level === 'error' ? 'text-red-600' : 'text-gray-700'}>{l.message}</span>
                        </div>
                    ))}
                </div>
            </div>

            {status?.status === 'draft_ready' && (
                <div className="flex justify-end">
                    <button onClick={() => navigate(`/projects/${id}/draft`)} className="btn-primary">
                        View Draft <ArrowRight className="w-5 h-5 ml-2" />
                    </button>
                </div>
            )}
        </div>
    )
}
