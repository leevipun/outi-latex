"""Database helper functions for managing schema and data."""

import os

from sqlalchemy import text

from src.config import app, db


def reset_db():
    """Drop all tables created by the schema to fully reset the database."""
    tables_to_drop = [
        "user_ref",
        "reference_tags",
        "reference_values",
        "single_reference",
        "reference_type_fields",
        "fields",
        "tags",
        "users",
        "reference_types",
    ]

    for table in tables_to_drop:
        print(f"Dropping {table} table")
        sql = text(f"DROP TABLE IF EXISTS {table} CASCADE")
        db.session.execute(sql)
        db.session.commit()


def tables():
    """Return all table names from the database except those ending with _id_seq."""
    sql = text(
        "SELECT table_name "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public' "
        "AND table_name NOT LIKE '%_id_seq'"
    )

    result = db.session.execute(sql)
    return [row[0] for row in result.fetchall()]


def setup_db():
    """Create the database schema.

    If database tables already exist, those are dropped before the creation.
    """
    tables_in_db = tables()
    if len(tables_in_db) > 0:
        print(f"Tables exist, dropping: {', '.join(tables_in_db)}")
        for table in tables_in_db:
            sql = text(f"DROP TABLE {table} CASCADE")
            db.session.execute(sql)
        db.session.commit()

    print("Creating database")

    # Read schema from schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read().strip()

    sql = text(schema_sql)
    db.session.execute(sql)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        setup_db()
