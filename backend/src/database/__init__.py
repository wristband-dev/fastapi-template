"""
Database — PostgreSQL via SQLModel/SQLAlchemy.

Local dev: Docker PostgreSQL (see docker-compose.yml)
Cloud: Cloud SQL PostgreSQL (connected via Cloud SQL Proxy)
"""

import logging
import sys

from sqlmodel import SQLModel, text, create_engine
from sqlalchemy import Engine

from environment import environment as env


logger = logging.getLogger(__name__)


_engine: Engine | None = None


# =============================================================================
# MARK: Public
# =============================================================================


def get_engine() -> Engine | None:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        if env.database_url:
            _engine = create_engine(
                env.database_url,
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
            )
    return _engine


def test_connection():
    """Test database connection and show current database."""
    engine = get_engine()

    logger.info(f"Environment: {env.type.value}")
    logger.info(f"Database URL: {'set' if env.database_url else 'NOT SET'}")

    if not engine:
        logger.error("No database connection")
        sys.exit(1)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user"))
            row = result.fetchone()
            if row:
                logger.info(f"Connected to: {row[0]} (user: {row[1]})")
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)


def rebuild():
    """Drop all tables, recreate them, and set up permissions."""
    reset_tables()
    create_tables()
    setup_permissions()
    tables = list_tables()
    for table in tables:
        list_columns(table)


def query(sql: str, params: dict | None = None) -> list[dict]:
    """Execute raw SQL and return rows as dicts."""
    engine = get_engine()
    if not engine:
        raise RuntimeError("No database connection")
    with engine.connect() as conn:
        logger.info(f"Executing SQL: {sql}")
        result = conn.execute(text(sql), params or {})
        rows = result.fetchall()
    return [row._asdict() for row in rows]


def list_tables() -> list[str]:
    """List all tables in the database."""
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        return []

    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    logger.info(f"Tables ({len(tables)}):")
    for table in tables:
        logger.info(f"  - {table}")

    return tables


def list_columns(table_name: str) -> list:
    """List columns and their types for a table."""
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        return []

    from sqlalchemy import inspect
    inspector = inspect(engine)

    try:
        columns = inspector.get_columns(table_name)
    except Exception as e:
        logger.error(f"Table '{table_name}' not found: {e}")
        return []

    logger.info(f"Columns in '{table_name}' ({len(columns)}):")
    for col in columns:
        nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get("default") else ""
        logger.info(f"  - {col['name']}: {col['type']} {nullable}{default}")

    return columns


def get_rows(table_name: str) -> list[dict]:
    """Get all rows from a table."""
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        return []

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()
        return [row._asdict() for row in rows]


def drop_records(table_name: str) -> int:
    """Delete all rows from a table. Returns the number of rows deleted."""
    engine = get_engine()
    if not engine:
        raise RuntimeError("No database connection")
    with engine.connect() as conn:
        logger.info(f"Deleting all rows from '{table_name}'")
        result = conn.execute(text(f"DELETE FROM {table_name}"))
        conn.commit()
        count = result.rowcount
        logger.info(f"Deleted {count} row(s) from '{table_name}'")
        return count


# =============================================================================
# MARK: Infrastructure
# =============================================================================


def register_models():
    """Import all schema models to register them with SQLModel.

    Add new model imports here as you create them.
    Must be called before any metadata operations (create_all, drop_all).
    """
    from database.schema.customer_schema import CustomerDB  # noqa: F401
    from database.schema.secret_schema import SecretDB  # noqa: F401


def setup_permissions():
    """Grant permissions to all users (including IAM users) on public schema.

    Safe to run multiple times — grants are idempotent.
    """
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        return

    with engine.connect() as conn:
        conn.execute(text("GRANT USAGE ON SCHEMA public TO PUBLIC"))
        conn.execute(
            text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO PUBLIC")
        )
        conn.execute(
            text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO PUBLIC")
        )
        conn.execute(
            text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC")
        )
        conn.execute(
            text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO PUBLIC")
        )
        conn.commit()

    logger.info("Permissions granted to all users")


def create_tables():
    """Create all tables and set up permissions."""
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        return

    register_models()
    logger.info("Creating tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tables created")


def reset_tables():
    """Drop and recreate all tables."""
    engine = get_engine()
    if not engine:
        logger.error("No database connection")
        sys.exit(1)

    register_models()
    logger.info("Dropping all tables...")

    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()

    create_tables()
