from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

class GoogleAuth(BaseModel):
    """User google token."""
    google_token: str

class UserAccount(BaseModel):
    """Return user account."""
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    profile_pic: Optional[str] = None

class GetAnalytics(BaseModel):
    """Get User Analytics"""
    created_at: datetime
    google_id: str
    duration: int
    full_date: datetime

class UserSettings(BaseModel):
    """User Settings Update"""
    display_time: Optional[str] = None
    timer_time: Optional[str] = None
    timer_end_notification: Optional[bool] = None
    timer_show_timer_on_browser_tab: Optional[bool] = None
    timer_web_notification: Optional[bool] = None
    timer_sessions: Optional[int] = None
    timer_auto_start: Optional[bool] = None
    timer_break_end_notification: Optional[bool] = None
    preference_shuffle_time: Optional[int] = None
    preference_background_color: Optional[str] = None
    daily_goal: Optional[int] = None

class Analytics(BaseModel):
    """Save analytics."""
    duration: int

class CreateTask(BaseModel):
    """Save analytics."""
    task_description: str
    duration: int

class Account(BaseModel):
    """Update user account"""
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None

class User(BaseModel):
    email: str
    google_id: str
    exp: int

class DictPayload(BaseModel):
    created_at: date
    google_id: str
    given_name: str
    family_name: str
    email: str
    profile_pic: str
    email_verified: str
