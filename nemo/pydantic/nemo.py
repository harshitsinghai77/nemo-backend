from datetime import datetime
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

    display_time: Optional[str]
    timer_time: Optional[str]
    timer_end_notification: Optional[bool]
    timer_show_timer_on_browser_tab: Optional[bool]
    timer_web_notification: Optional[bool]
    timer_sessions: Optional[int]
    timer_auto_start: Optional[bool]
    timer_break_end_notification: Optional[bool]
    preference_shuffle_time: Optional[str]
    preference_background_color: Optional[str]
    daily_goal: Optional[int]


class Analytics(BaseModel):
    """Save analytics."""

    duration: int


class Account(BaseModel):
    """Update user account"""

    given_name: str
    family_name: str
    username: str
    email: str
