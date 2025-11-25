"""Integration tests for src/utils/tags.py module."""

import pytest

from src.utils.tags import (
    TagError,
    TagExistsError,
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
