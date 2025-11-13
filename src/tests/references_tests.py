"""Test suite for reference management utilities."""

# pylint: disable=redefined-outer-name,wrong-import-position
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import app
from utils.references import get_all_references, get_all_added_references


@pytest.fixture
def test_app():
    """Create and configure a new app instance for each test."""
    app.config["TESTING"] = True
    return app


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@patch("utils.references.db")
def test_get_all_references_returns_correct_data(mock_db):
    """Test that get_all_references returns all reference types with correct data."""
    mock_rows = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
        {"id": 3, "name": "inproceedings"},
        {"id": 4, "name": "inbook"},
        {"id": 5, "name": "incollection"},
        {"id": 6, "name": "misc"},
        {"id": 7, "name": "phdthesis"},
        {"id": 8, "name": "mastersthesis"},
        {"id": 9, "name": "techreport"},
        {"id": 10, "name": "unpublished"},
    ]
    mock_db.session.execute.return_value.mappings.return_value = mock_rows

    result = get_all_references()

    expected = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
        {"id": 3, "name": "inproceedings"},
        {"id": 4, "name": "inbook"},
        {"id": 5, "name": "incollection"},
        {"id": 6, "name": "misc"},
        {"id": 7, "name": "phdthesis"},
        {"id": 8, "name": "mastersthesis"},
        {"id": 9, "name": "techreport"},
        {"id": 10, "name": "unpublished"},
    ]

    assert result == expected


@patch("utils.references.db")
def test_get_all_references_returns_list(mock_db):
    """Test that get_all_references returns a list."""
    mock_db.session.execute.return_value.mappings.return_value = []

    result = get_all_references()
    assert isinstance(result, list)


@patch("utils.references.db")
def test_get_all_references_ordered_by_id(mock_db):
    """Test that results are ordered by id."""
    mock_rows = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
        {"id": 3, "name": "inproceedings"},
    ]
    mock_db.session.execute.return_value.mappings.return_value = mock_rows

    result = get_all_references()
    ids = [item["id"] for item in result]
    assert ids == sorted(ids)


@patch("utils.references.db")
def test_get_all_references_has_correct_length(mock_db):
    """Test that all 10 reference types are returned."""
    mock_rows = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
        {"id": 3, "name": "inproceedings"},
        {"id": 4, "name": "inbook"},
        {"id": 5, "name": "incollection"},
        {"id": 6, "name": "misc"},
        {"id": 7, "name": "phdthesis"},
        {"id": 8, "name": "mastersthesis"},
        {"id": 9, "name": "techreport"},
        {"id": 10, "name": "unpublished"},
    ]
    mock_db.session.execute.return_value.mappings.return_value = mock_rows

    result = get_all_references()
    assert len(result) == 10


@patch("utils.references.db")
def test_get_all_references_dict_structure(mock_db):
    """Test that each item has 'id' and 'name' keys."""
    mock_rows = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
    ]
    mock_db.session.execute.return_value.mappings.return_value = mock_rows

    result = get_all_references()

    for item in result:
        assert isinstance(item, dict)
        assert "id" in item
        assert "name" in item
        assert isinstance(item["id"], int)
        assert isinstance(item["name"], str)


@patch("utils.references.db")
def test_get_all_references_empty_table(mock_db):
    """Test behavior when reference_types table is empty."""
    mock_db.session.execute.return_value.mappings.return_value = []

    result = get_all_references()
    assert not result


class TestGetAllAddedReferences:
    """Test suite for get_all_added_references function."""

    @patch("utils.references.db")
    def test_get_all_added_references_returns_list(self, mock_db):
        """Test that get_all_added_references returns a list."""
        mock_db.session.execute.return_value.mappings.return_value = []

        result = get_all_added_references()

        assert isinstance(result, list)

    @patch("utils.references.db")
    def test_get_all_added_references_empty_database(self, mock_db):
        """Test behavior when no references exist in database."""
        mock_db.session.execute.return_value.mappings.return_value = []

        result = get_all_added_references()

        assert not result

    @patch("utils.references.db")
    def test_get_all_added_references_single_reference_no_fields(self, mock_db):
        """Test with a single reference that has no field values."""
        mock_row = {
            "id": 1,
            "bib_key": "einstein1905",
            "reference_type": "article",
            "created_at": "2025-01-01 10:00:00",
            "key_name": None,
            "value": None,
        }
        mock_db.session.execute.return_value.mappings.return_value = [mock_row]

        result = get_all_added_references()

        expected = [
            {
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "fields": {},
            }
        ]
        assert result == expected

    @patch("utils.references.db")
    def test_get_all_added_references_single_ref_with_fields(self, mock_db):
        """Test with single reference that has multiple field values."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "author",
                "value": "Albert Einstein",
            },
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "title",
                "value": "On the Electrodynamics of Moving Bodies",
            },
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "year",
                "value": "1905",
            },
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        expected = [
            {
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "fields": {
                    "author": "Albert Einstein",
                    "title": "On the Electrodynamics of Moving Bodies",
                    "year": "1905",
                },
            }
        ]
        assert result == expected

    @patch("utils.references.db")
    def test_get_all_added_references_multiple_references(self, mock_db):
        """Test with multiple references."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-02 10:00:00",
                "key_name": "author",
                "value": "Albert Einstein",
            },
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-02 10:00:00",
                "key_name": "title",
                "value": "Relativity",
            },
            {
                "id": 2,
                "bib_key": "darwin1859",
                "reference_type": "book",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "author",
                "value": "Charles Darwin",
            },
            {
                "id": 2,
                "bib_key": "darwin1859",
                "reference_type": "book",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "title",
                "value": "On the Origin of Species",
            },
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        assert len(result) == 2
        assert result[0]["bib_key"] == "einstein1905"
        assert result[1]["bib_key"] == "darwin1859"

    @patch("utils.references.db")
    def test_get_all_added_references_ordered_by_created_at(self, mock_db):
        """Test that results are ordered by created_at descending."""
        mock_rows = [
            {
                "id": 2,
                "bib_key": "darwin1859",
                "reference_type": "book",
                "created_at": "2025-01-02 10:00:00",
                "key_name": None,
                "value": None,
            },
            {
                "id": 1,
                "bib_key": "einstein1905",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": None,
                "value": None,
            },
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        # Should be ordered by created_at descending
        assert result[0]["created_at"] == "2025-01-02 10:00:00"
        assert result[1]["created_at"] == "2025-01-01 10:00:00"

    @patch("utils.references.db")
    def test_get_all_added_references_dict_structure(self, mock_db):
        """Test that each reference has required keys."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "misc",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "note",
                "value": "Test note",
            }
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        assert len(result) == 1
        item = result[0]
        assert isinstance(item, dict)
        assert "bib_key" in item
        assert "reference_type" in item
        assert "created_at" in item
        assert "fields" in item
        assert isinstance(item["fields"], dict)

    @patch("utils.references.db")
    def test_get_all_added_references_field_values_can_be_null(self, mock_db):
        """Test that field values can be None/null."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "misc",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "note",
                "value": None,
            }
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        assert result[0]["fields"]["note"] is None

    @patch("utils.references.db")
    def test_get_all_added_references_groups_by_ref_id(self, mock_db):
        """Test that rows with same reference ID are grouped together."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "author",
                "value": "John Doe",
            },
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "journal",
                "value": "Science",
            },
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        assert len(result) == 1
        assert len(result[0]["fields"]) == 2
        assert result[0]["fields"]["author"] == "John Doe"
        assert result[0]["fields"]["journal"] == "Science"

    @patch("utils.references.db")
    def test_get_all_added_references_preserves_field_order(self, mock_db):
        """Test that field values are preserved correctly."""
        mock_rows = [
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "title",
                "value": "Test Article",
            },
            {
                "id": 1,
                "bib_key": "test2025",
                "reference_type": "article",
                "created_at": "2025-01-01 10:00:00",
                "key_name": "author",
                "value": "Test Author",
            },
        ]
        mock_db.session.execute.return_value.mappings.return_value = mock_rows

        result = get_all_added_references()

        assert result[0]["fields"]["title"] == "Test Article"
        assert result[0]["fields"]["author"] == "Test Author"
