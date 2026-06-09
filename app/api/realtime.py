"""
Real-time user activity tracking and WebSocket endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.services.realtime_service import RealtimeService
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/v1/realtime", tags=["Real-time"])

# Store active WebSocket connections
active_connections: dict[int, List[WebSocket]] = {}


@router.post("/session/start")
def session_start(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new user session for activity tracking
    
    Returns: session_id and session_token
    """
    try:
        session_data = RealtimeService.create_session(db, current_user.id, current_user.username)
        RealtimeService.set_user_online(db, current_user.id, current_user.username)
        
        return {
            "status": "success",
            "session_id": session_data.get("session_id"),
            "session_token": session_data.get("session_token"),
            "user_id": current_user.id,
            "username": current_user.username
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activity/log")
def log_activity(
    activity_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log user activity
    
    Expected fields:
    - action_type: "query" | "download" | "view" | "upload" | etc
    - resource: name of resource being accessed
    - query_params: optional dict of parameters
    - duration_ms: milliseconds spent on activity
    """
    try:
        log_entry = RealtimeService.log_activity(
            db,
            current_user.id,
            activity_data.get("action_type"),
            activity_data.get("resource"),
            activity_data.get("query_params", {}),
            activity_data.get("duration_ms", 0)
        )
        
        return {
            "status": "success",
            "activity_id": log_entry.get("id"),
            "message": "Activity logged"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/online-users")
def get_online_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of currently online users (admin only)
    """
    try:
        online_users = RealtimeService.get_online_users(db)
        
        return {
            "status": "success",
            "count": len(online_users),
            "users": [
                {
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "last_seen": user.get("last_seen"),
                    "session_duration": user.get("session_duration")
                }
                for user in online_users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/end")
def session_end(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End the current user session
    """
    try:
        RealtimeService.set_user_offline(db, current_user.id)
        RealtimeService.end_session(db, current_user.id)
        
        return {
            "status": "success",
            "message": "Session ended",
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-activity/{user_id}")
def get_user_activity(
    user_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity history for a user (admin only)
    """
    try:
        activity = RealtimeService.get_user_activity(db, user_id, limit)
        
        return {
            "status": "success",
            "user_id": user_id,
            "count": len(activity),
            "activities": activity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-sessions")
def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active user sessions (admin only)
    """
    try:
        sessions = RealtimeService.get_active_sessions(db)
        
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time activity tracking
    
    Usage:
    - Connect: ws://localhost:8000/api/v1/realtime/ws/{user_id}
    - Send: {"action": "activity", "data": {...}}
    - Receive: {"type": "activity", "from": user_id, "data": {...}}
    """
    await websocket.accept()
    
    # Add connection to active connections
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("action") == "activity":
                # Broadcast to all connected clients
                activity_data = {
                    "type": "activity",
                    "from": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": data.get("data", {})
                }
                
                for connection in active_connections.get(user_id, []):
                    try:
                        await connection.send_json(activity_data)
                    except Exception:
                        pass
            
            elif data.get("action") == "heartbeat":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        # Remove connection
        if user_id in active_connections:
            active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
    
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if user_id in active_connections and websocket in active_connections[user_id]:
            active_connections[user_id].remove(websocket)
