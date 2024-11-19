from alembic import context
from database.models import (
    Task,  # noqa: F401
    User,  # noqa: F401
    Project,  # noqa: F401
    TaskLog,  # noqa: F401
    project_developers_table,  # noqa: F401
)
from database.models.mapper import mapper_registry
from database.adapters.mysql import MySQL

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
