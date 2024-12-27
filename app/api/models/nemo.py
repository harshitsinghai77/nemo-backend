from datetime import datetime
from typing import Optional

from sqlmodel import Field, Index, SQLModel

class NemoUserInformation(SQLModel, table=True):
    __tablename__ = "nemo_user_information"

    google_id: str = Field(primary_key=True)
    email: str
    given_name: str
    family_name: Optional[str] = None
    profile_pic: Optional[str] = None
    email_verified: bool = Field(default=False)
    username: str = Field(default="")
    created_at: datetime


class NemoSettings(SQLModel, table=True):
    __tablename__ = "nemo_settings"

    google_id: str = Field(
        foreign_key="nemo_user_information.google_id",
        ondelete="CASCADE",
        primary_key=True,
    )
    timer_time: str = Field(default="2700")
    display_time: str = Field(default="45 : 00")
    timer_end_notification: bool = Field(default=False)
    timer_show_timer_on_browser_tab: bool = Field(default=False)
    timer_web_notification: bool = Field(default=False)
    timer_sessions: int = Field(default=4)
    timer_auto_start: bool = Field(default=False)
    timer_break_end_notification: bool = Field(default=False)
    preference_shuffle_time: int = Field(default=10)
    preference_background_color: str = Field(default="rainbow")
    daily_goal: int = Field(default=4)


class NemoAnalytics(SQLModel, table=True):
    __tablename__ = "nemo_analytics"

    id: int = Field(default=None, primary_key=True)
    google_id: str = Field(foreign_key="nemo_user_information.google_id")
    created_at: datetime
    duration: int  # in seconds
    full_date: datetime

    __table_args__ = (Index("ix_analytics_google_id", "google_id"),)


class NemoTasks(SQLModel, table=True):
    __tablename__ = "nemo_tasks"

    id: int = Field(default=None, primary_key=True)
    google_id: str = Field(foreign_key="nemo_user_information.google_id")
    created_at: datetime
    task_description: str
    duration: int  # in seconds
    task_date: datetime

    __table_args__ = (Index("ix_tasks_google_id", "google_id"),)
