from sqlalchemy import Float, Table, Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from core.models.log import Log
from database.models.mapper import mapper_registry

task_log_table = Table(
    "task_log",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("timestamp", BigInteger, nullable=False),
    Column("task_id", String(26), ForeignKey("task.id"), nullable=False),
    Column("task_name", String(100), nullable=False),
    Column("description", String(255), nullable=True),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("user_name", String(50), nullable=False),
    Column("project_id", String(26), ForeignKey("project.id"), nullable=False),
    Column("project_name", String(100), nullable=False),
    Column("hours_spent_today", Float, nullable=False),
    Column("task_status", String(50), nullable=False),
)

mapper_registry.map_imperatively(
    Log,
    task_log_table,
    properties={
        "task": relationship(
            "Task",
            back_populates="logs",
            lazy="noload",
        ),
        "user": relationship(
            "User",
            back_populates="task_logs",
            lazy="noload",
        ),
    },
)
