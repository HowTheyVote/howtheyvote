from alembic import context

from howtheyvote.config import DATABASE_URI

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URI)


def run_migrations_online() -> None:
    connection = config.attributes.get("connection", None)
    context.configure(connection=connection, target_metadata=None)

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
