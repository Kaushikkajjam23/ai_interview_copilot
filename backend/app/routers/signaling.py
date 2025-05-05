from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
import json

from ..database import get_db
from ..models.interview import InterviewSession

router = APIRouter(
    prefix="/ws",
    tags=["signaling"],
)

# Store active connections
class ConnectionManager:
    def __init__(self):
        # Map session_id -> {role -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, role: str):
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        self.active_connections[session_id][role] = websocket
    
    def disconnect(self, session_id: str, role: str):
        if session_id in self.active_connections and role in self.active_connections[session_id]:
            del self.active_connections[session_id][role]
            
            # Clean up empty sessions
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, role: str, message: str):
        if session_id in self.active_connections and role in self.active_connections[session_id]:
            await self.active_connections[session_id][role].send_text(message)
    
    async def broadcast_to_session(self, session_id: str, sender_role: str, message: str):
        if session_id in self.active_connections:
            for role, connection in self.active_connections[session_id].items():
                if role != sender_role:  # Don't send back to sender
                    await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/interview/{session_id}/{role}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    role: str
):
    # Validate session exists
    db = next(get_db())
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        await websocket.close(code=1008, reason="Interview session not found")
        return
    
    # Validate role
    if role not in ["interviewer", "candidate"]:
        await websocket.close(code=1008, reason="Invalid role")
        return
    
    # Accept connection
    await manager.connect(websocket, session_id, role)
    
    try:
        while True:
            # Receive message from this client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add sender role to the message
            message_data["sender"] = role
            
            # Forward to other participants in the same session
            await manager.broadcast_to_session(
                session_id, 
                role, 
                json.dumps(message_data)
            )
    except WebSocketDisconnect:
        manager.disconnect(session_id, role)
        # Notify other participants
        disconnect_message = json.dumps({
            "type": "user-disconnected",
            "sender": role
        })
        await manager.broadcast_to_session(session_id, role, disconnect_message)