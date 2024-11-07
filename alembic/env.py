from alembic import context
from database.models.mapper import mapper_registry
from src.database.adapters.mysql import MySQL
from src.database.models.task_mapper import Task  # noqa
from src.database.models.user_mapper import User  # noqa
from src.database.models.project_mapper import Project  # noqa
from src.database.models.task_log_mapper import TaskLog  # noqa
from src.database.models.association_tables import (
    project_developers_table,  # noqa
)

target_metadata = mapper_registry.metadata

registries = [mapper_registry]

for registry in registries:
    for table in registry.metadata.tables.values():
        print(f"Adding table {table.name} to metadata")
        table.tometadata(target_metadata)


def run_migrations_online():
    connectable = MySQL.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
