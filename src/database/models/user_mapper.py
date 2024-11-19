from sqlalchemy import Table, Column, String, BigInteger
from sqlalchemy.orm import relationship

from core.models.user import User
from database.models.mapper import mapper_registry
from database.models.association_tables import project_developers_table

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("email", String(50)),
    Column("password", String(150)),
    Column("full_name", String(50)),
    Column("permissions", BigInteger),
)


mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "projects": relationship(
            "Project",
            secondary=project_developers_table,
            back_populates="developers",
            lazy="joined",
        ),
        "tasks": relationship(
            "Task",
            back_populates="user",
            cascade="all, delete-orphan",
            lazy="joined",
        ),
        "task_logs": relationship(
            "TaskLog",
            back_populates="user",
            cascade="all, delete-orphan",
            lazy="joined",
        ),
    },
)
