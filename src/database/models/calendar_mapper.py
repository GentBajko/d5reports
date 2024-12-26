from sqlalchemy import Boolean, Date, Table, Column, String, ForeignKey

from core.models.office_calendar import OfficeCalendar
from database.models.mapper import mapper_registry

remote_day_table = Table(
    "remote_days",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("day", Date, nullable=False),
    Column("present", Boolean, nullable=True, default=False),
)

mapper_registry.map_imperatively(OfficeCalendar, remote_day_table)
