import sys
import os
from pathlib import Path

# Add src directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from config import db, app
from utils.references import get_all_references
from sqlalchemy import text


@pytest.fixture
def test_app():
    """Create and configure a new app instance for each test."""
    app.config['TESTING'] = True
    return app


@pytest.fixture
def setup_test_db(test_app):
    """Set up test database with sample data, cleaning up before and after."""
    with test_app.app_context():
        # Clean up existing data first
        try:
            db.session.execute(text("TRUNCATE TABLE reference_types CASCADE"))
            # Reset the sequence
            db.session.execute(text("ALTER SEQUENCE reference_types_id_seq RESTART WITH 1"))
            db.session.commit()
        except:
            # Table might not exist, that's okay
            db.session.rollback()
        
        # Insert test data
        reference_data = [
            ('article',),
            ('book',),
            ('inproceedings',),
            ('inbook',),
            ('incollection',),
            ('misc',),
            ('phdthesis',),
            ('mastersthesis',),
            ('techreport',),
            ('unpublished',),
        ]
        
        sql = text("INSERT INTO reference_types (name) VALUES (:name)")
        for data in reference_data:
            db.session.execute(sql, {"name": data[0]})
        db.session.commit()
        
        yield
        
        # Cleanup after test
        try:
            db.session.execute(text("TRUNCATE TABLE reference_types CASCADE"))
            db.session.commit()
        except:
            db.session.rollback()


def test_get_all_references_returns_correct_data(setup_test_db):
    """Test that get_all_references returns all reference types with correct data."""
    with app.app_context():
        result = get_all_references()
        
        expected = [
            {'id': 1, 'name': 'article'},
            {'id': 2, 'name': 'book'},
            {'id': 3, 'name': 'inproceedings'},
            {'id': 4, 'name': 'inbook'},
            {'id': 5, 'name': 'incollection'},
            {'id': 6, 'name': 'misc'},
            {'id': 7, 'name': 'phdthesis'},
            {'id': 8, 'name': 'mastersthesis'},
            {'id': 9, 'name': 'techreport'},
            {'id': 10, 'name': 'unpublished'}
        ]
        
        assert result == expected


def test_get_all_references_returns_list(setup_test_db):
    """Test that get_all_references returns a list."""
    with app.app_context():
        result = get_all_references()
        assert isinstance(result, list)


def test_get_all_references_ordered_by_id(setup_test_db):
    """Test that results are ordered by id."""
    with app.app_context():
        result = get_all_references()
        ids = [item['id'] for item in result]
        assert ids == sorted(ids)


def test_get_all_references_has_correct_length(setup_test_db):
    """Test that all 10 reference types are returned."""
    with app.app_context():
        result = get_all_references()
        assert len(result) == 10


def test_get_all_references_dict_structure(setup_test_db):
    """Test that each item has 'id' and 'name' keys."""
    with app.app_context():
        result = get_all_references()
        
        for item in result:
            assert isinstance(item, dict)
            assert 'id' in item
            assert 'name' in item
            assert isinstance(item['id'], int)
            assert isinstance(item['name'], str)


def test_get_all_references_empty_table(test_app):
    """Test behavior when reference_types table is empty."""
    with test_app.app_context():
        # Clean the table
        try:
            db.session.execute(text("TRUNCATE TABLE reference_types CASCADE"))
            db.session.commit()
        except:
            db.session.rollback()
        
        result = get_all_references()
        assert result == []
