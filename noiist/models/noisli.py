from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, Text

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
    Column("email", Text, unique=True),
    Column("profile_pic", Text),
    Column("email_verified", Boolean, server_default="False"),
)
