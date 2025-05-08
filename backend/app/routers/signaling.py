from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import logging

from ..database import get_db
from ..models.interview import InterviewSession

# Set up logging
logger = logging.getLogger(__name__)

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
        # Check if this role already has a connection for this session
        if (session_id in self.active_connections and 
            role in self.active_connections[session_id]):
            logger.warning(f"Replacing existing connection for session {session_id}, role {role}")
            # Close the existing connection
            try:
                await self.active_connections[session_id][role].close(
                    code=1008, 
                    reason="New connection established for this role"
                )
            except Exception as e:
                logger.error(f"Error closing existing connection: {e}")
        
        await websocket.accept()
        logger.info(f"WebSocket connection established for session {session_id}, role {role}")
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][role] = websocket
    
    def disconnect(self, session_id: str, role: str):
        if session_id in self.active_connections:
            if role in self.active_connections[session_id]:
                logger.info(f"WebSocket disconnected for session {session_id}, role {role}")
                del self.active_connections[session_id][role]
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_message(self, message: str, session_id: str, role: str):
        if session_id in self.active_connections:
            roles = list(self.active_connections[session_id].keys())
            for r in roles:
                if r != role:  # Send to the other role
                    try:
                        await self.active_connections[session_id][r].send_text(message)
                        logger.debug(f"Message sent to session {session_id}, role {r}")
                    except Exception as e:
                        logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_session(self, session_id: str, sender_role: str, message: str):
        if session_id in self.active_connections:
            for role, connection in self.active_connections[session_id].items():
                if role != sender_role:  # Don't send back to sender
                    try:
                        await connection.send_text(message)
                        logger.debug(f"Message broadcast to session {session_id}, role {role}")
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@router.websocket("/interview/{session_id}/{role}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    role: str,
    db: Session = Depends(get_db)
):
    try:
        # Validate session exists
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            logger.warning(f"WebSocket connection attempt for non-existent session: {session_id}")
            await websocket.close(code=1008, reason="Interview session not found")
            return
        
        # Validate role
        if role not in ["interviewer", "candidate"]:
            logger.warning(f"WebSocket connection attempt with invalid role: {role}")
            await websocket.close(code=1008, reason="Invalid role")
            return
        
        # Accept connection
        await manager.connect(websocket, session_id, role)
        
        # Send initial connection notification to other participant
        connect_message = json.dumps({
            "type": "user-connected",
            "sender": role
        })
        await manager.broadcast_to_session(session_id, role, connect_message)
        
        while True:
            # Receive message from this client
            data = await websocket.receive_text()
            
            try:
                # Validate JSON format
                message_data = json.loads(data)
                
                # Add sender role to the message if not present
                if "sender" not in message_data:
                    message_data["sender"] = role
                
                # Forward to other participants in the same session
                await manager.broadcast_to_session(
                    session_id, 
                    role, 
                    json.dumps(message_data)
                )
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                # Forward raw message as fallback
                await manager.broadcast_to_session(session_id, role, data)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}, role {role}")
        manager.disconnect(session_id, role)
        # Notify other participants
        disconnect_message = json.dumps({
            "type": "user-disconnected",
            "sender": role
        })
        await manager.broadcast_to_session(session_id, role, disconnect_message)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id, role)

# backend/app/routers/signaling.py
@router.websocket("/test")
async def test_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_text("Hello from server")
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass