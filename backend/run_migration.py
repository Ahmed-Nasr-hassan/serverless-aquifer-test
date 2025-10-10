"""
One-off migration script to switch primary/foreign keys to UUID.

This will DROP existing tables (users, models, simulations) and recreate
them with UUID columns according to the current SQLAlchemy models.

WARNING: This is destructive and intended for development environments.
"""

from sqlalchemy import text
from database import engine
from database import create_tables

SQL_ENABLE_EXTENSIONS = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
"""

SQL_DROP_TABLES = """
DROP TABLE IF EXISTS simulations CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS users CASCADE;
"""

def main() -> None:
    with engine.begin() as conn:
        # Ensure UUID extensions exist
        conn.execute(text(SQL_ENABLE_EXTENSIONS))
        # Drop old tables
        conn.execute(text(SQL_DROP_TABLES))

    # Recreate tables with current models (UUID columns)
    create_tables()
    print("✅ Migration complete: tables recreated with UUID columns.")


if __name__ == "__main__":
    main()


