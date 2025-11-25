"""Integration tests for src/utils/tags.py module."""

import pytest

from src.utils.tags import (
    add_tag_to_reference,
    delete_tag_from_reference,
    get_tag_by_reference,
    get_tags,
    add_tag,
)


class TestAddTagToReference:
    """Tests for add_tag_to_reference function."""

    def test_add_tag_to_reference_success(self, app):
        """Test adding a tag to a reference successfully."""
        with app.app_context():
            tag_id = add_tag("Test Tag")
            reference_id = 1 

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
            reference_id = 2

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
            reference_id = 3

            add_tag_to_reference(tag_id, reference_id)
            delete_tag_from_reference(reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is None

    def test_delete_tag_from_reference_no_existing_tag(self, app):
        """Test deleting a tag from a reference that has no tag."""
        with app.app_context():
            reference_id = 4

            # Ensure no exception is raised when deleting non-existing tag
            delete_tag_from_reference(reference_id)
            tag = get_tag_by_reference(reference_id)

            assert tag is None


class TestGetTagByReference:
    """Tests for get_tag_by_reference function."""

    def test_get_tag_by_reference_no_tag(self, app):
        """Test getting a tag for a reference with no tag."""
        with app.app_context():
            reference_id = 5
            tag = get_tag_by_reference(reference_id)

            assert tag is None

    def test_get_tag_by_reference_with_tag(self, app):
        """Test getting a tag for a reference that has a tag."""
        with app.app_context():
            tag_id = add_tag("Existing Tag")
            reference_id = 6

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
