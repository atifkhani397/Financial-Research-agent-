"""
ARA-1 WebSocket Streaming Server (Day 16)
Streams live Thought/Action/Observation execution traces to frontend clients.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.schemas import TraceEvent

logger = logging.getLogger("ara1.api.websocket")
router = APIRouter(tags=["WebSocket Streaming"])


class ConnectionManager:
    """Manages active WebSocket connections per session ID."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.trace_history: Dict[str, List[dict]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
            self.trace_history[session_id] = []
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket client connected to session={session_id}")

        # Send existing trace history upon connection
        for event in self.trace_history.get(session_id, []):
            await websocket.send_text(json.dumps(event))

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session={session_id}")

    async def broadcast_event(self, session_id: str, event: dict):
        if session_id not in self.trace_history:
            self.trace_history[session_id] = []
        self.trace_history[session_id].append(event)

        if session_id in self.active_connections:
            event_json = json.dumps(event)
            for connection in list(self.active_connections[session_id]):
                try:
                    await connection.send_text(event_json)
                except Exception as e:
                    logger.warning(f"Error broadcasting WebSocket message: {e}")


ws_manager = ConnectionManager()


@router.websocket("/ws/research/{session_id}")
async def websocket_research_trace(websocket: WebSocket, session_id: str):
    """WebSocket endpoint streaming real-time ReAct trace events."""
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            # Keep connection alive and accept client pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.warning(f"WebSocket error in session={session_id}: {e}")
        ws_manager.disconnect(session_id, websocket)
