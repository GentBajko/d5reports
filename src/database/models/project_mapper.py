from sqlalchemy import Table, Column, String, Boolean
from sqlalchemy.orm import relationship

from core.models.project import Project
from database.models.mapper import mapper_registry
from database.models.association_tables import project_developers_table

project_table = Table(
    "project",
    mapper_registry.metadata,
    Column("id", String(26), primary_key=True),
    Column("name", String(100), nullable=False),
    Column("email", String(50), nullable=False),
    Column("send_email", Boolean, default=False),
    Column("archived", Boolean, default=False),
)

mapper_registry.map_imperatively(
    Project,
    project_table,
    properties={
        "developers": relationship(
            "User",
            secondary=project_developers_table,
            back_populates="projects",
            lazy="noload",
        ),
        "tasks": relationship(
            "Task",
            back_populates="project",
            cascade="all, delete-orphan",
            lazy="noload",
        ),
    },
)
