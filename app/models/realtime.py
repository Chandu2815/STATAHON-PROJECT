"""
Real-time tracking models for user sessions, activities, and analytics
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class UserSession(Base):
    """Track active user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    username = Column(String(100), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_end = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, username={self.username}, is_active={self.is_active})>"


class ActivityLog(Base):
    """Track user activities and actions"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # query, download, view, upload, etc
    resource = Column(String(255), nullable=False)  # dataset name, table name, etc
    query_params = Column(JSON, nullable=True)  # parameters used in the action
    duration_ms = Column(Integer, default=0)  # how long the action took
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ActivityLog(user_id={self.user_id}, action_type={self.action_type}, resource={self.resource})>"


class AnalyticsEvent(Base):
    """Track analytics events for business intelligence"""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # page_view, button_click, search, etc
    event_data = Column(JSON, nullable=True)  # custom data for the event
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AnalyticsEvent(user_id={self.user_id}, event_type={self.event_type})>"


class OnlineUser(Base):
    """Track currently online users"""
    __tablename__ = "online_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False)
    is_online = Column(Boolean, default=True, index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OnlineUser(user_id={self.user_id}, username={self.username}, is_online={self.is_online})>"
