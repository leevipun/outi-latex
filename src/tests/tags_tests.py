"""Integration tests for src/utils/tags.py module."""

from src.utils.references import add_reference
from src.utils.tags import (
    add_tag,
    add_tag_to_reference,
    delete_tag_from_reference,
    get_tag_by_reference,
    get_tags,
)


class TestAddTagToReference:
    """Tests for add_tag_to_reference function."""

    def test_add_tag_to_reference_success(self, app):
        """Test adding a tag to a reference successfully."""
        with app.app_context():
            tag_id = add_tag("Test Tag")
            data = {
                "bib_key": "Test2025",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "2025",
            }
            reference_id = add_reference("article", data)

            add_tag_to_reference(tag_id, reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is not None
            assert tag["id"] == tag_id
            assert tag["name"] == "Test Tag"

    def test_add_tag_to_reference_replace_existing(self, app):
        """Test replacing an existing tag on a reference."""
        with app.app_context():
            first_tag_id = add_tag("First Tag")
            second_tag_id = add_tag("Second Tag")
            data = {
                "bib_key": "Test2021",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "2021",
            }
            reference_id = add_reference("article", data)

            add_tag_to_reference(first_tag_id, reference_id)
            add_tag_to_reference(second_tag_id, reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is not None
            assert tag["id"] == second_tag_id
            assert tag["name"] == "Second Tag"


class TestDeleteTagFromReference:
    """Tests for delete_tag_from_reference function."""

    def test_delete_tag_from_reference_success(self, app):
        """Test deleting a tag from a reference successfully."""
        with app.app_context():
            tag_id = add_tag("Tag to Delete")
            data = {
                "bib_key": "Test2019",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "2019",
            }
            reference_id = add_reference("article", data)

            add_tag_to_reference(tag_id, reference_id)
            delete_tag_from_reference(reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is None

    def test_delete_tag_from_reference_no_existing_tag(self, app):
        """Test deleting a tag from a reference that has no tag."""
        with app.app_context():
            data = {
                "bib_key": "Test1984",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "1984",
            }
            reference_id = add_reference("article", data)

            # Ensure no exception is raised when deleting non-existing tag
            delete_tag_from_reference(reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is None


class TestGetTagByReference:
    """Tests for get_tag_by_reference function."""

    def test_get_tag_by_reference_no_tag(self, app):
        """Test getting a tag for a reference with no tag."""
        with app.app_context():
            data = {
                "bib_key": "Test2026",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "2026",
            }
            reference_id = add_reference("article", data)
            tag = get_tag_by_reference(reference_id)

            assert tag is None

    def test_get_tag_by_reference_with_tag(self, app):
        """Test getting a tag for a reference that has a tag."""
        with app.app_context():
            tag_id = add_tag("Existing Tag")
            data = {
                "bib_key": "Test1987",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "1987",
            }
            reference_id = add_reference("article", data)

            add_tag_to_reference(tag_id, reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is not None
            assert tag["id"] == tag_id
            assert tag["name"] == "Existing Tag"


class TestGetTags:
    """Tests for get_tags function."""

    def test_get_tags_returns_all_tags(self, app):
        """Test that get_tags returns all tags in the database."""
        with app.app_context():
            tag_names = ["Tag One", "Tag Two", "Tag Three"]
            for name in tag_names:
                add_tag(name)

            tags = get_tags()
            retrieved_tag_names = [tag["name"] for tag in tags]

            for name in tag_names:
                assert name in retrieved_tag_names
