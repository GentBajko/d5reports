from ulid import ULID
from sqlalchemy import Table, Column, String, ForeignKey, UniqueConstraint

from database.models.mapper import mapper_registry
from core.models.project_user import ProjectUser

project_developers_table = Table(
    "project_developers",
    mapper_registry.metadata,
    Column(
        "id", String(26), primary_key=True, nullable=False, default=str(ULID())
    ),
    Column("user_id", String(26), ForeignKey("user.id"), nullable=False),
    Column("project_id", String(26), ForeignKey("project.id"), nullable=False),
    UniqueConstraint("user_id", "project_id", name="uix_user_project"),
)

mapper_registry.map_imperatively(
    ProjectUser,
    project_developers_table,
)
