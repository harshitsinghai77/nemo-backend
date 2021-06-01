from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, Text

from noiist.config.database import metadata

user = Table(
    "core_user",
    metadata,
    Column("created_at", DateTime),
    Column("id", Integer, primary_key=True, unique=True),
    Column("email", String, unique=True),
    Column("display_name", String(length=255)),
    Column("spotify_url", Text),
    Column("access_token", Text),
    Column("refresh_token", Text),
    Column("is_active", Boolean, server_default="False"),
)
