from sqlalchemy import Table, Column, String, ForeignKey

from database.models.mapper import mapper_registry
from core.models.project_user import ProjectUser

project_developers_table = Table(
    "project_developers",
    mapper_registry.metadata,
    Column("user_id", String(26), ForeignKey("user.id"), primary_key=True),
    Column(
        "project_id", String(26), ForeignKey("project.id"), primary_key=True
    ),
)

mapper_registry.map_imperatively(
    ProjectUser,
    project_developers_table,
)
