"""Unit tests for filtering and sorting references."""

from datetime import datetime
from src.utils.references import (
    sort_references_by_created_at,
    sort_references_by_field,
    sort_references_by_bib_key
)

class TestSortReferences:
    """Test sorting functions."""

    def test_sort_by_created_at_newest(self):
        """Test sorting by creation date, newest first."""
        refs = [
            {"bib_key": "ref1", "created_at": datetime(2024, 1, 1)},
            {"bib_key": "ref3", "created_at": datetime(2024, 3, 1)},
            {"bib_key": "ref2", "created_at": datetime(2024, 2, 1)},
        ]

        sorted_refs = sort_references_by_created_at(refs, "newest")

        assert sorted_refs[0]["bib_key"] == "ref3"
        assert sorted_refs[1]["bib_key"] == "ref2"
        assert sorted_refs[2]["bib_key"] == "ref1"

    def test_sort_by_created_at_oldest(self):
        """Test sorting by creation date, oldest first."""
        refs = [
            {"bib_key": "ref1", "created_at": datetime(2024, 1, 1)},
            {"bib_key": "ref3", "created_at": datetime(2024, 3, 1)},
            {"bib_key": "ref2", "created_at": datetime(2024, 2, 1)},
        ]

        sorted_refs = sort_references_by_created_at(refs, "oldest")

        assert sorted_refs[0]["bib_key"] == "ref1"
        assert sorted_refs[1]["bib_key"] == "ref2"
        assert sorted_refs[2]["bib_key"] == "ref3"

    def test_sort_by_field_title_asc(self):
        """Test sorting by title field in ascending order."""
        refs = [
            {"bib_key": "ref1", "fields": {"title": "Zebra"}},
            {"bib_key": "ref2", "fields": {"title": "Apple"}},
            {"bib_key": "ref3", "fields": {"title": "Banana"}},
        ]

        sorted_refs = sort_references_by_field(refs, "title", "asc")

        assert sorted_refs[0]["fields"]["title"] == "Apple"
        assert sorted_refs[1]["fields"]["title"] == "Banana"
        assert sorted_refs[2]["fields"]["title"] == "Zebra"

    def test_sort_by_field_author_asc(self):
        """Test sorting by author field in ascending order."""
        refs = [
            {"bib_key": "ref1", "fields": {"author": "Smith"}},
            {"bib_key": "ref2", "fields": {"author": "Adams"}},
            {"bib_key": "ref3", "fields": {"author": "Johnson"}},
        ]

        sorted_refs = sort_references_by_field(refs, "author", "asc")

        assert sorted_refs[0]["fields"]["author"] == "Adams"
        assert sorted_refs[1]["fields"]["author"] == "Johnson"
        assert sorted_refs[2]["fields"]["author"] == "Smith"

    def test_sort_by_bib_key_asc(self):
        """Test sorting by bib_key in ascending order."""
        refs = [
            {"bib_key": "zebra2024"},
            {"bib_key": "apple2023"},
            {"bib_key": "banana2024"},
        ]

        sorted_refs = sort_references_by_bib_key(refs, "asc")

        assert sorted_refs[0]["bib_key"] == "apple2023"
        assert sorted_refs[1]["bib_key"] == "banana2024"
        assert sorted_refs[2]["bib_key"] == "zebra2024"

    def test_sort_empty_list(self):
        """Test sorting empty list returns empty list."""
        assert sort_references_by_created_at([], "newest") == []
        assert sort_references_by_field([], "title", "asc") == []
        assert sort_references_by_bib_key([], "asc") == []

