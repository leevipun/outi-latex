"""Integration tests for src/utils/references.py module."""

import pytest

from src.utils.references import (
    DatabaseError,
    add_reference,
    delete_reference_by_bib_key,
    get_all_added_references,
    get_all_references,
    get_reference_by_bib_key,
)


class TestGetAllReferences:
    """Tests for get_all_references function."""

    def test_returns_all_reference_types(self, app, db_session):
        """Test that all seeded reference types are returned."""
        with app.app_context():
            result = get_all_references()
            assert len(result) == 3
            names = {ref["name"] for ref in result}
            assert names == {"article", "book", "inproceedings"}

    def test_returns_sorted_by_id(self, app, db_session):
        """Test that reference types are sorted by ID."""
        with app.app_context():
            result = get_all_references()
            ids = [ref["id"] for ref in result]
            assert ids == sorted(ids)

    def test_returns_dict_with_id_and_name(self, app, db_session):
        """Test that each reference type has id and name."""
        with app.app_context():
            result = get_all_references()
            for ref_type in result:
                assert "id" in ref_type
                assert "name" in ref_type
                assert isinstance(ref_type["id"], int)
                assert isinstance(ref_type["name"], str)


class TestAddReference:
    """Tests for add_reference function."""

    def test_add_reference_successfully(self, app, db_session, sample_reference_data):
        """Test adding a reference successfully."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            # Verify it was added
            result = get_all_added_references()
            assert len(result) == 1
            assert result[0]["bib_key"] == "Smith2020"
            assert result[0]["reference_type"] == "article"

    def test_add_reference_with_all_fields(
        self, app, db_session, sample_reference_data
    ):
        """Test that all fields are stored correctly."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            result = get_all_added_references()
            ref = result[0]["fields"]

            assert ref["author"] == "John Smith"
            assert ref["title"] == "A Great Paper"
            assert ref["journal"] == "Journal of Examples"
            assert ref["year"] == "2020"  # Stored as string

    def test_add_reference_skips_empty_values(self, app, db_session):
        """Test that empty values are not stored."""
        with app.app_context():
            data = {
                "bib_key": "Test2020",
                "author": "Test Author",
                "title": "Test Title",
                "journal": None,
                "year": "",
            }
            add_reference("article", data)

            result = get_all_added_references()
            ref = result[0]["fields"]

            assert "author" in ref
            assert "title" in ref
            assert "journal" not in ref  # None values excluded
            assert "year" not in ref  # Empty strings excluded

    def test_add_reference_unknown_type_raises_error(self, app, db_session):
        """Test that unknown reference type raises DatabaseError."""
        with app.app_context():
            data = {
                "bib_key": "Test2020",
                "author": "Test Author",
                "title": "Test Title",
            }

            with pytest.raises(DatabaseError) as exc_info:
                add_reference("unknown_type", data)

            assert "Unknown reference type" in str(exc_info.value)

    def test_add_multiple_references(self, app, db_session, sample_reference_data):
        """Test adding multiple references."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            data2 = {
                "bib_key": "Johnson2021",
                "author": "Jane Johnson",
                "title": "Another Paper",
                "journal": "Different Journal",
                "year": 2021,
            }
            add_reference("article", data2)

            result = get_all_added_references()
            assert len(result) == 2
            bib_keys = {ref["bib_key"] for ref in result}
            assert bib_keys == {"Smith2020", "Johnson2021"}

    def test_add_references_of_different_types(self, app, db_session):
        """Test adding references of different types."""
        with app.app_context():
            article_data = {
                "bib_key": "Article2020",
                "author": "Author A",
                "title": "Article Title",
                "journal": "A Journal",
                "year": 2020,
            }

            book_data = {
                "bib_key": "Book2020",
                "author": "Author B",
                "title": "Book Title",
                "publisher": "A Publisher",
                "year": 2020,
            }

            add_reference("article", article_data)
            add_reference("book", book_data)

            result = get_all_added_references()
            assert len(result) == 2

            types = {ref["reference_type"] for ref in result}
            assert types == {"article", "book"}

    def test_add_reference_with_special_characters(self, app, db_session):
        """Test adding reference with special characters."""
        with app.app_context():
            data = {
                "bib_key": "Müller2020",
                "author": "Dr. Müller & Co.",
                "title": 'Test\'s "Special" Title',
                "journal": "Journal (International)",
                "year": 2020,
            }

            add_reference("article", data)

            result = get_all_added_references()
            ref = result[0]["fields"]
            assert ref["author"] == "Dr. Müller & Co."
            assert '"Special"' in ref["title"]


class TestGetAllAddedReferences:
    """Tests for get_all_added_references function."""

    def test_returns_empty_list_initially(self, app, db_session):
        """Test that empty database returns empty list."""
        with app.app_context():
            result = get_all_added_references()
            assert result == []

    def test_returns_added_reference(self, app, db_session, sample_reference_data):
        """Test retrieving added reference."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            result = get_all_added_references()
            assert len(result) == 1
            assert result[0]["bib_key"] == "Smith2020"
            assert result[0]["reference_type"] == "article"
            assert "fields" in result[0]
            assert "created_at" in result[0]

    def test_returns_fields_correctly_grouped(
        self, app, db_session, sample_reference_data
    ):
        """Test that fields are grouped correctly per reference."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            result = get_all_added_references()
            fields = result[0]["fields"]

            assert isinstance(fields, dict)
            assert len(fields) > 0
            for key, value in fields.items():
                assert isinstance(key, str)
                assert isinstance(value, str)

    def test_sorted_by_created_at_descending(self, app, db_session):
        """Test that results are sorted by created_at descending."""
        with app.app_context():
            data1 = {
                "bib_key": "First2020",
                "author": "Author 1",
                "title": "First",
                "journal": "J1",
                "year": 2020,
            }

            data2 = {
                "bib_key": "Second2020",
                "author": "Author 2",
                "title": "Second",
                "journal": "J2",
                "year": 2020,
            }

            add_reference("article", data1)
            add_reference("article", data2)

            result = get_all_added_references()

            # Most recent first
            assert result[0]["bib_key"] == "Second2020"
            assert result[1]["bib_key"] == "First2020"

    def test_contains_all_required_fields(self, app, db_session, sample_reference_data):
        """Test that returned reference has all required fields."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            result = get_all_added_references()
            ref = result[0]

            assert "bib_key" in ref
            assert "reference_type" in ref
            assert "created_at" in ref
            assert "fields" in ref

    def test_created_at_is_datetime(self, app, db_session, sample_reference_data):
        """Test that created_at is a datetime object."""
        from datetime import datetime

        with app.app_context():
            add_reference("article", sample_reference_data)

            result = get_all_added_references()
            assert isinstance(result[0]["created_at"], datetime)


class TestIntegrationWorkflows:
    """Integration tests combining multiple functions."""

    def test_full_workflow_add_and_retrieve(
        self, app, db_session, sample_reference_data
    ):
        """Test complete workflow: get types -> add reference -> retrieve all."""
        with app.app_context():
            # Step 1: Get available types
            types = get_all_references()
            assert len(types) > 0

            # Step 2: Add reference
            add_reference("article", sample_reference_data)

            # Step 3: Retrieve all references
            references = get_all_added_references()
            assert len(references) == 1
            assert references[0]["bib_key"] == "Smith2020"

    def test_add_multiple_different_types_workflow(self, app, db_session):
        """Test workflow with multiple reference types."""
        with app.app_context():
            # Get all types
            types = get_all_references()
            type_names = {t["name"] for t in types}
            assert "article" in type_names
            assert "book" in type_names

            # Add article
            article_data = {
                "bib_key": "Art2020",
                "author": "A",
                "title": "Article",
                "journal": "J",
                "year": 2020,
            }
            add_reference("article", article_data)

            # Add book
            book_data = {
                "bib_key": "Book2020",
                "author": "B",
                "title": "Book",
                "publisher": "P",
                "year": 2020,
            }
            add_reference("book", book_data)

            # Retrieve all
            refs = get_all_added_references()
            assert len(refs) == 2

            # Verify types
            ref_types = {r["reference_type"] for r in refs}
            assert ref_types == {"article", "book"}


class TestGetReferenceByBibKey:
    """Tests for get_reference_by_bib_key function."""

    def test_get_existing_reference(self, app, sample_reference_data):
        """Test retrieving an existing reference by bib_key."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            ref = get_reference_by_bib_key("Smith2020")
            assert ref is not None
            assert ref["bib_key"] == "Smith2020"
            assert ref["reference_type"] == "article"
            assert "fields" in ref
            assert ref["fields"]["author"] == "John Smith"

    def test_get_nonexistent_reference_returns_none(self, app):
        """Test that retrieving a non-existent bib_key returns None."""
        with app.app_context():
            ref = get_reference_by_bib_key("NonExistentKey")
            assert ref is None

    def test_get_reference_after_deletion(self, app, db_session, sample_reference_data):
        """Test that a reference cannot be retrieved after deletion."""
        with app.app_context():
            add_reference("article", sample_reference_data)

            # Ensure it exists
            ref = get_reference_by_bib_key("Smith2020")
            assert ref is not None

            # Delete it
            delete_reference_by_bib_key("Smith2020")

            # Now it should return None
            ref_after = get_reference_by_bib_key("Smith2020")
            assert ref_after is None


class TestDeleteReference:
    """Tests for delete_reference_by_bib_key function."""

    def test_delete_reference_removes_from_db(
        self, app, db_session, sample_reference_data
    ):
        """Adding then deleting a reference removes it from DB."""
        with app.app_context():
            # Add a reference first
            add_reference("article", sample_reference_data)

            # Sanity: it exists
            ref = get_reference_by_bib_key("Smith2020")
            assert ref is not None

            # Delete it
            delete_reference_by_bib_key("Smith2020")

            # Now it shouldn't exist
            ref_after = get_reference_by_bib_key("Smith2020")
            assert ref_after is None

            # And get_all_added_references should be empty
            all_refs = get_all_added_references()
            assert all_refs == []

    def test_delete_reference_also_deletes_values_via_cascade(
        self, app, db_session, sample_reference_data
    ):
        """Deleting from single_reference removes related reference_values (ON DELETE CASCADE)."""
        from sqlalchemy import text

        from src.config import db

        with app.app_context():
            # Add reference
            add_reference("article", sample_reference_data)

            # Get its id
            ref = get_reference_by_bib_key("Smith2020")
            ref_id = ref["id"]

            # There should be some rows in reference_values for this reference
            count_before = db.session.execute(
                text("SELECT COUNT(*) FROM reference_values WHERE reference_id = :rid"),
                {"rid": ref_id},
            ).scalar()
            assert count_before > 0

            # Delete using our helper
            delete_reference_by_bib_key("Smith2020")

            # Now no reference_values rows for that id should remain
            count_after = db.session.execute(
                text("SELECT COUNT(*) FROM reference_values WHERE reference_id = :rid"),
                {"rid": ref_id},
            ).scalar()
            assert count_after == 0
