from sqlalchemy import Table, Column, String, ForeignKey

from src.database.models.mapper import mapper_registry

project_developers_table = Table(
    "project_developers",
    mapper_registry.metadata,
    Column("user_id", String(26), ForeignKey("user.id"), primary_key=True),
    Column(
        "project_id", String(26), ForeignKey("project.id"), primary_key=True
    ),
)