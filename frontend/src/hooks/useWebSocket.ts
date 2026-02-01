import { useEffect, useState, useRef, useCallback } from 'react'

interface WebSocketMessage {
    type: string
    agent?: string
    step?: string
    status?: string
    message?: string
    progress?: number
    url?: string
    title?: string
    domain?: string
    credibility_score?: number
    data?: object
}

export function useWebSocket(projectId: string) {
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
    const [isConnected, setIsConnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws/${projectId}`

        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
            setIsConnected(true)
            console.log('WebSocket connected')
        }

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)
                if (message.type !== 'heartbeat' && message.type !== 'pong') {
                    setLastMessage(message)
                }
            } catch (e) {
                console.error('Failed to parse WebSocket message', e)
            }
        }

        ws.onclose = () => {
            setIsConnected(false)
            console.log('WebSocket disconnected')
            // Reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(connect, 3000)
        }

        ws.onerror = (error) => {
            console.error('WebSocket error', error)
        }
    }, [projectId])

    useEffect(() => {
        connect()

        // Send ping every 25 seconds to keep connection alive
        const pingInterval = setInterval(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: 'ping' }))
            }
        }, 25000)

        return () => {
            clearInterval(pingInterval)
            clearTimeout(reconnectTimeoutRef.current)
            wsRef.current?.close()
        }
    }, [connect])

    return { lastMessage, isConnected }
}
