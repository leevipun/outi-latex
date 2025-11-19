"""Pytest configuration for tests."""

import os
import sys

# Add the src directory to the path BEFORE any test imports
# This must run at module import time, not in fixtures
src_path = os.path.join(os.path.dirname(__file__), "..")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest
from sqlalchemy import text


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Import app to register all routes
    from src import app as app_module  # noqa: F401
    from src.config import app as flask_app

    # Set testing mode
    flask_app.config["TESTING"] = True

    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a test database session and setup/teardown."""
    from src.config import db
    from src.db_helper import setup_db

    with app.app_context():
        # Setup test database schema
        setup_db()

        # Seed reference types
        sql = text(
            """
            INSERT INTO reference_types (name) VALUES
            ('article'),
            ('book'),
            ('inproceedings')
        """
        )
        db.session.execute(sql)
        db.session.commit()

        # Seed fields for articles
        article_fields = [
            ("author", "str", "text"),
            ("title", "str", "text"),
            ("journal", "str", "text"),
            ("year", "int", "number"),
            ("volume", "int", "number"),
            ("number", "int", "number"),
            ("pages", "str", "text"),
            ("doi", "str", "text"),
            ("url", "str", "text"),
        ]

        for key_name, data_type, input_type in article_fields:
            sql = text(
                """
                INSERT INTO fields (key_name, data_type, input_type) 
                VALUES (:key_name, :data_type, :input_type)
            """
            )
            db.session.execute(
                sql,
                {
                    "key_name": key_name,
                    "data_type": data_type,
                    "input_type": input_type,
                },
            )

        db.session.commit()

        # Link fields to article type
        sql = text(
            """
            INSERT INTO reference_type_fields (reference_type_id, field_id, required)
            SELECT 1, f.id, CASE WHEN f.key_name IN ('author', 'title', 'journal', 'year') THEN TRUE ELSE FALSE END
            FROM fields f
        """
        )
        db.session.execute(sql)

        # Link fields to book type
        book_fields = [
            ("author", "str", "text"),
            ("title", "str", "text"),
            ("publisher", "str", "text"),
            ("year", "int", "number"),
        ]

        for key_name, data_type, input_type in book_fields:
            sql = text(
                """
                SELECT id FROM fields WHERE key_name = :key_name
            """
            )
            result = db.session.execute(sql, {"key_name": key_name}).scalar()
            if result:
                sql = text(
                    """
                    INSERT INTO reference_type_fields (reference_type_id, field_id, required)
                    VALUES (2, :field_id, CASE WHEN :key_name IN ('author', 'title', 'publisher', 'year') THEN TRUE ELSE FALSE END)
                """
                )
                db.session.execute(sql, {"field_id": result, "key_name": key_name})

        db.session.commit()

        yield db

        # Cleanup after test
        db.session.rollback()


@pytest.fixture
def sample_reference_data():
    """Fixture providing sample reference data."""
    return {
        "bib_key": "Smith2020",
        "author": "John Smith",
        "title": "A Great Paper",
        "journal": "Journal of Examples",
        "year": 2020,
        "volume": 5,
        "number": 3,
        "pages": "100-115",
    }
