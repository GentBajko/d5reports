from sqlalchemy import Date, Table, Column, String, ForeignKey

from core.models.remote import RemoteDay
from database.models.mapper import mapper_registry


remote_day_table = Table(
    "remote_days",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("day", Date, nullable=False),
)

mapper_registry.map_imperatively(RemoteDay, remote_day_table)
