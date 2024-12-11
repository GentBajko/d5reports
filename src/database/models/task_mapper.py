from sqlalchemy import Float, Table, Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from core.models.task import Task
from database.models.mapper import mapper_registry
from sqlalchemy.orm import column_property
from sqlalchemy.sql import select, func
from core.models.log import Log

task_table = Table(
    "task",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("project_id", String(26), ForeignKey("project.id"), nullable=False),
    Column("project_name", String(100), nullable=False),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("user_name", String(100), nullable=False),
    Column("title", String(100), nullable=False),
    Column("hours_required", Float, nullable=False),
    Column("description", String(255), nullable=True),
    Column("status", String(50), nullable=True),
    Column("timestamp", BigInteger, nullable=False),
    Column("hours_worked", Float, nullable=False, default=0.0),
)

mapper_registry.map_imperatively(
    Task,
    task_table,
    properties={
        "project": relationship(
            "Project",
            back_populates="tasks",
            lazy="noload",
        ),
        "user": relationship(
            "User",
            back_populates="tasks",
            lazy="noload",
        ),
        "logs": relationship(
            "Log",
            back_populates="task",
            cascade="all, delete-orphan",
            lazy="noload",
        ),
        "last_updated": column_property(
            select(func.max(Log.timestamp)) # type: ignore
            .where(Log.task_id == task_table.c.id) # type: ignore
            .correlate_except(Log)
            .scalar_subquery()
        ),
    },
)
