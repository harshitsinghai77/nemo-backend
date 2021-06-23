from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
    Text,
    ForeignKey,
)

from noiist.config.database import metadata

noisli_user = Table(
    "core_noisli_user",
    metadata,
    Column("created_at", DateTime),
    Column("id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column(
        "google_id", String, primary_key=True, unique=True, nullable=False
    ),  # The unique ID of the user's Google Account
    Column("given_name", String(length=255), nullable=False),
    Column("family_name", String(length=255)),
    Column("username", String(length=255)),
    Column("email", Text, unique=True),
    Column("profile_pic", Text),
    Column("email_verified", Boolean, server_default="False"),
)

noisli_user_settings = Table(
    "core_noisli_settings",
    metadata,
    Column("google_id", ForeignKey("core_noisli_user.google_id")),
    Column("timer_time", String, server_default="45"),
    Column("timer_end_notification", Boolean, server_default="False"),
    Column("timer_show_timer_on_browser_tab", Boolean, server_default="False"),
    Column("timer_web_notification", Boolean, server_default="False"),
    Column("timer_sessions", Integer, server_default="4"),
    Column("timer_auto_start", Boolean, server_default="False"),
    Column("timer_break_end_notification", Boolean, server_default="False"),
    Column("preference_shuffle_time", String, server_default="10"),
    Column("preference_background_color", String, server_default="rainbow"),
)
