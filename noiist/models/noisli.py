from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, Text

from noiist.config.database import metadata

noisli_user = Table(
    "core_noisli_user",
    metadata,
    Column("created_at", DateTime),
    Column("id", Integer, primary_key=True, unique=True),
    Column("name", String(length=255), nullable=False),
    Column("email", Text, unique=True),
    Column("profile_pic", Text),
    Column("is_active", Boolean, server_default="False"),
)
