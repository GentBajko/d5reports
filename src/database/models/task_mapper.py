from sqlalchemy import Float, Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from core.models.task import Task
from database.models.mapper import mapper_registry

task_table = Table(
    "task",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("project_id", String(26), ForeignKey("project.id"), nullable=False),
    Column("project_name", String(100), nullable=False),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("title", String(100), nullable=False),
    Column("hours_required", Float, nullable=False),
    Column("description", String(255), nullable=True),
    Column("status", String(50), nullable=False),
)

mapper_registry.map_imperatively(
    Task,
    task_table,
    properties={
        "project": relationship(
            "Project",
            back_populates="tasks",
            lazy="joined",
        ),
        "user": relationship(
            "User",
            back_populates="tasks",
            lazy="joined",
        ),
        "logs": relationship(
            "TaskLog",
            back_populates="task",
            cascade="all, delete-orphan",
            lazy="joined",
        ),
    },
)
