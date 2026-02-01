"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.core.logging import get_logger

router = APIRouter(tags=["websocket"])
logger = get_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections per project."""

    def __init__(self):
        # Map project_id to set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        logger.info("websocket_connected", project_id=project_id)

    def disconnect(self, project_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        logger.info("websocket_disconnected", project_id=project_id)

    async def send_to_project(self, project_id: str, message: dict) -> None:
        """Send a message to all connections for a project."""
        if project_id not in self.active_connections:
            return
        
        dead_connections = set()
        
        for connection in self.active_connections[project_id]:
            try:
                if connection.application_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_send_error", error=str(e))
                dead_connections.add(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.active_connections[project_id].discard(connection)

    async def broadcast_agent_update(
        self,
        project_id: str,
        agent: str,
        step: str,
        status: str,
        message: str,
        progress: float = 0.0,
        data: dict = None,
    ) -> None:
        """Broadcast an agent update to all project connections."""
        await self.send_to_project(project_id, {
            "type": "agent_update",
            "agent": agent,
            "step": step,
            "status": status,
            "message": message,
            "progress": progress,
            "data": data or {},
        })

    async def broadcast_source_discovered(
        self,
        project_id: str,
        url: str,
        title: str,
        domain: str,
        credibility_score: float,
    ) -> None:
        """Broadcast a new source discovery."""
        await self.send_to_project(project_id, {
            "type": "source_discovered",
            "url": url,
            "title": title,
            "domain": domain,
            "credibility_score": credibility_score,
        })

    async def broadcast_draft_update(
        self,
        project_id: str,
        section: str,
        content: str,
        word_count: int,
    ) -> None:
        """Broadcast draft section update."""
        await self.send_to_project(project_id, {
            "type": "draft_update",
            "section": section,
            "content": content,
            "word_count": word_count,
        })


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for project updates."""
    await manager.connect(project_id, websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # Heartbeat timeout
                )
                
                # Handle client messages (e.g., ping)
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e), project_id=project_id)
        manager.disconnect(project_id, websocket)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
