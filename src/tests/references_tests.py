"""Test suite for reference management utilities."""

# pylint: disable=redefined-outer-name,wrong-import-position
from unittest.mock import MagicMock, patch

import pytest

from src.config import app
from src.utils.references import get_all_added_references, get_all_references


@pytest.fixture
def test_app():
    """Create and configure a new app instance for each test."""
    app.config["TESTING"] = True
    return app


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@patch("src.utils.references.db")
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


@patch("src.utils.references.db")
def test_get_all_references_returns_list(mock_db):
    """Test that get_all_references returns a list."""
    mock_db.session.execute.return_value.mappings.return_value = []

    result = get_all_references()
    assert isinstance(result, list)


@patch("src.utils.references.db")
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


@patch("src.utils.references.db")
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


@patch("src.utils.references.db")
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


@patch("src.utils.references.db")
def test_get_all_references_empty_table(mock_db):
    """Test behavior when reference_types table is empty."""
    mock_db.session.execute.return_value.mappings.return_value = []

    result = get_all_references()
    assert not result


class TestGetAllAddedReferences:
    """Test suite for get_all_added_references function."""

    @patch("src.utils.references.db")
    def test_get_all_added_references_returns_list(self, mock_db):
        """Test that get_all_added_references returns a list."""
        mock_db.session.execute.return_value.mappings.return_value = []

        result = get_all_added_references()

        assert isinstance(result, list)

    @patch("src.utils.references.db")
    def test_get_all_added_references_empty_database(self, mock_db):
        """Test behavior when no references exist in database."""
        mock_db.session.execute.return_value.mappings.return_value = []

        result = get_all_added_references()

        assert not result

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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

    @patch("src.utils.references.db")
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


class TestAddReference:
    """Test suite for add_reference function."""

    @patch("src.utils.references.db")
    def test_add_reference_successful_insert(self, mock_db):
        """Test successful insertion of a reference with basic fields."""
        # Mock the reference type lookup
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        # Mock the insert reference
        insert_result = MagicMock()
        insert_result.scalar.return_value = 42

        # Mock the field lookup
        field_result = MagicMock()
        field_result.mappings.return_value.first.return_value = {"id": 10}

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference
            field_result,  # Field lookup for "author"
            MagicMock(),  # Insert reference_values for author
            field_result,  # Field lookup for "title"
            MagicMock(),  # Insert reference_values for title
        ]

        from src.utils.references import add_reference

        data = {
            "bib_key": "Einstein1905",
            "author": "Albert Einstein",
            "title": "On the Electrodynamics of Moving Bodies",
        }

        add_reference("article", data)

        mock_db.session.commit.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_unknown_reference_type(self, mock_db):
        """Test error when reference type does not exist."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = None

        mock_db.session.execute.return_value = type_result

        from src.utils.references import add_reference, DatabaseError

        data = {"bib_key": "test2025", "author": "Test Author"}

        with pytest.raises(DatabaseError) as exc_info:
            add_reference("unknown_type", data)

        assert "Unknown reference type" in str(exc_info.value)
        mock_db.session.rollback.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_skips_empty_values(self, mock_db):
        """Test that empty string and None values are skipped."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        insert_result = MagicMock()
        insert_result.scalar.return_value = 42

        field_result = MagicMock()
        field_result.mappings.return_value.first.return_value = {"id": 10}

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference
            field_result,  # Field lookup for "author"
            MagicMock(),  # Insert reference_values for author
        ]

        from src.utils.references import add_reference

        data = {
            "bib_key": "test2025",
            "author": "John Doe",
            "title": "",  # Should be skipped
            "year": None,  # Should be skipped
        }

        add_reference("article", data)

        # Only author field should be inserted (plus reference type and reference insert)
        assert mock_db.session.execute.call_count == 4
        mock_db.session.commit.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_skips_unknown_fields(self, mock_db):
        """Test that fields not in schema are skipped."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        insert_result = MagicMock()
        insert_result.scalar.return_value = 42

        # Field exists for "author" but not for "unknown_field"
        author_field = MagicMock()
        author_field.mappings.return_value.first.return_value = {"id": 10}

        unknown_field = MagicMock()
        unknown_field.mappings.return_value.first.return_value = None

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference
            author_field,  # Field lookup for "author"
            MagicMock(),  # Insert reference_values for author
            unknown_field,  # Field lookup for "unknown_field" - not found
        ]

        from src.utils.references import add_reference

        data = {
            "bib_key": "test2025",
            "author": "John Doe",
            "unknown_field": "some value",
        }

        add_reference("article", data)

        mock_db.session.commit.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_uses_scalar_for_new_id(self, mock_db):
        """Test that new reference ID is retrieved using scalar()."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        insert_result = MagicMock()
        insert_result.scalar.return_value = 99

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference with scalar() returning ID
        ]

        from src.utils.references import add_reference

        data = {"bib_key": "test2025"}

        add_reference("article", data)

        insert_result.scalar.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_fallback_to_mappings_for_id(self, mock_db):
        """Test fallback to mappings().first() when scalar() returns None."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        insert_result = MagicMock()
        insert_result.scalar.return_value = None  # scalar() returns None
        mappings_result = MagicMock()
        mappings_result.first.return_value = {"id": 55}
        insert_result.mappings.return_value = mappings_result

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference
        ]

        from src.utils.references import add_reference

        data = {"bib_key": "test2025"}

        add_reference("article", data)

        insert_result.scalar.assert_called_once()
        insert_result.mappings.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_rollback_on_exception(self, mock_db):
        """Test that rollback is called when an exception occurs."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 1}

        mock_db.session.execute.side_effect = [
            type_result,
            Exception("Database error"),  # Simulate database error
        ]

        from src.utils.references import add_reference, DatabaseError

        data = {"bib_key": "test2025"}

        with pytest.raises(DatabaseError):
            add_reference("article", data)

        mock_db.session.rollback.assert_called_once()

    @patch("src.utils.references.db")
    def test_add_reference_with_multiple_fields(self, mock_db):
        """Test adding reference with multiple field values."""
        type_result = MagicMock()
        type_result.mappings.return_value.first.return_value = {"id": 2}

        insert_result = MagicMock()
        insert_result.scalar.return_value = 123

        field_result = MagicMock()
        field_result.mappings.return_value.first.return_value = {"id": 10}

        mock_db.session.execute.side_effect = [
            type_result,  # Reference type lookup
            insert_result,  # Insert single_reference
            field_result,  # Field lookup for "author"
            MagicMock(),  # Insert reference_values for author
            field_result,  # Field lookup for "title"
            MagicMock(),  # Insert reference_values for title
            field_result,  # Field lookup for "year"
            MagicMock(),  # Insert reference_values for year
            field_result,  # Field lookup for "journal"
            MagicMock(),  # Insert reference_values for journal
        ]

        from src.utils.references import add_reference

        data = {
            "bib_key": "einstein1905",
            "author": "Albert Einstein",
            "title": "On the Electrodynamics of Moving Bodies",
            "year": "1905",
            "journal": "Annalen der Physik",
        }

        add_reference("article", data)

        mock_db.session.commit.assert_called_once()
        # 1 type lookup + 1 insert ref + (4 fields * 2 calls each) = 10 total calls
        assert mock_db.session.execute.call_count == 10

    @patch("src.utils.references.db")
    def test_add_reference_database_error_is_wrapped(self, mock_db):
        """Test that database errors are wrapped in DatabaseError."""
        mock_db.session.execute.side_effect = Exception("Connection lost")

        from src.utils.references import add_reference, DatabaseError

        data = {"bib_key": "test2025"}

        with pytest.raises(DatabaseError) as exc_info:
            add_reference("article", data)

        assert "Failed to insert reference" in str(exc_info.value)
        mock_db.session.rollback.assert_called_once()
