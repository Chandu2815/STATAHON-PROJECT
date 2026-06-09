"""
Real-time user activity tracking service
"""
from sqlalchemy.orm import Session
from app.models.realtime import UserSession, ActivityLog, AnalyticsEvent, OnlineUser
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class RealtimeService:
    """Service for real-time user activity tracking"""
    
    @staticmethod
    def create_session(db: Session, user_id: int, username: str) -> Dict:
        try:
            session = UserSession(
                user_id=user_id,
                username=username,
                session_start=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return {
                "session_id": session.id,
                "session_token": f"token_{session.id}_{user_id}",
                "user_id": user_id,
                "username": username
            }
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def log_activity(db: Session, user_id: int, action_type: str, resource: str, query_params: Dict = None, duration_ms: int = 0) -> Dict:
        try:
            activity = ActivityLog(
                user_id=user_id,
                action_type=action_type,
                resource=resource,
                query_params=query_params or {},
                duration_ms=duration_ms,
                timestamp=datetime.utcnow()
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)
            
            return {
                "id": activity.id,
                "user_id": user_id,
                "action_type": action_type,
                "timestamp": activity.timestamp.isoformat()
            }
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def log_analytics_event(db: Session, user_id: int, event_type: str, event_data: Dict = None) -> Dict:
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data or {},
                timestamp=datetime.utcnow()
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            return {"id": event.id, "user_id": user_id, "event_type": event_type}
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def set_user_online(db: Session, user_id: int, username: str) -> Dict:
        try:
            online_user = db.query(OnlineUser).filter(OnlineUser.user_id == user_id).first()
            
            if online_user:
                online_user.last_seen = datetime.utcnow()
                online_user.is_online = True
            else:
                online_user = OnlineUser(
                    user_id=user_id,
                    username=username,
                    is_online=True,
                    last_seen=datetime.utcnow()
                )
                db.add(online_user)
            
            db.commit()
            db.refresh(online_user)
            
            return {"user_id": user_id, "username": username, "is_online": True}
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def set_user_offline(db: Session, user_id: int) -> Dict:
        try:
            online_user = db.query(OnlineUser).filter(OnlineUser.user_id == user_id).first()
            
            if online_user:
                online_user.is_online = False
                online_user.last_seen = datetime.utcnow()
                db.commit()
                db.refresh(online_user)
            
            return {"user_id": user_id, "is_online": False}
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_online_users(db: Session) -> List[Dict]:
        try:
            online_users = db.query(OnlineUser).filter(OnlineUser.is_online == True).all()
            
            return [
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "last_seen": user.last_seen.isoformat() if user.last_seen else None,
                    "session_duration": (datetime.utcnow() - user.last_seen).total_seconds() if user.last_seen else 0
                }
                for user in online_users
            ]
        except Exception as e:
            raise e
    
    @staticmethod
    def end_session(db: Session, user_id: int) -> Dict:
        try:
            session = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                session.session_end = datetime.utcnow()
                db.commit()
                db.refresh(session)
                
                return {
                    "session_id": session.id,
                    "user_id": user_id,
                    "duration_seconds": (session.session_end - session.session_start).total_seconds()
                }
            
            return {"status": "no_active_session"}
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_user_activity(db: Session, user_id: int, limit: int = 50) -> List[Dict]:
        try:
            activities = db.query(ActivityLog).filter(
                ActivityLog.user_id == user_id
            ).order_by(ActivityLog.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "id": activity.id,
                    "action_type": activity.action_type,
                    "resource": activity.resource,
                    "duration_ms": activity.duration_ms,
                    "timestamp": activity.timestamp.isoformat()
                }
                for activity in activities
            ]
        except Exception as e:
            raise e
    
    @staticmethod
    def get_active_sessions(db: Session) -> List[Dict]:
        try:
            sessions = db.query(UserSession).filter(UserSession.is_active == True).all()
            
            return [
                {
                    "session_id": session.id,
                    "user_id": session.user_id,
                    "username": session.username,
                    "session_start": session.session_start.isoformat(),
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "duration_seconds": (datetime.utcnow() - session.session_start).total_seconds()
                }
                for session in sessions
            ]
        except Exception as e:
            raise e
