# C:\Users\kajjam_kaushik\ai_interview_copilot\backend\alembic\env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool, text
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from alembic import context
from app.database import SQLALCHEMY_DATABASE_URL
from app.models import interview, user
from app.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Configure SQLite to support foreign keys
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Add this for SQLite batch operations
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Enable SQLite foreign keys - use text() to create a proper SQL expression
        connection.execute(text("PRAGMA foreign_keys=ON"))
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Add this for SQLite batch operations
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()