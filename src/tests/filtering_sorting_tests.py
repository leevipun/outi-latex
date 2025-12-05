"""Unit tests for filtering and sorting references."""

from datetime import datetime

from src.utils.references import (
    filter_and_sort_search_results,
    sort_references_by_bib_key,
    sort_references_by_created_at,
    sort_references_by_field,
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


class TestFilterAndSortSearchResults:
    """Test filtering and sorting search results."""

    def test_filter_by_type(self):
        """Test filtering by reference type."""
        refs = [
            {
                "bib_key": "ref1",
                "reference_type": "article",
                "created_at": datetime(2024, 1, 1),
            },
            {
                "bib_key": "ref2",
                "reference_type": "book",
                "created_at": datetime(2024, 1, 2),
            },
            {
                "bib_key": "ref3",
                "reference_type": "article",
                "created_at": datetime(2024, 1, 3),
            },
        ]

        filtered = filter_and_sort_search_results(refs, ref_type_filter="article")

        assert len(filtered) == 2
        assert all(ref["reference_type"] == "article" for ref in filtered)

    def test_filter_by_tag(self):
        """Test filtering by tag."""
        refs = [
            {
                "bib_key": "ref1",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 1),
            },
            {
                "bib_key": "ref2",
                "tag": {"id": 2, "name": "ML"},
                "created_at": datetime(2024, 1, 2),
            },
            {
                "bib_key": "ref3",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 3),
            },
            {"bib_key": "ref4", "tag": None, "created_at": datetime(2024, 1, 4)},
        ]

        filtered = filter_and_sort_search_results(refs, tag_filter="AI")

        assert len(filtered) == 2
        assert all(ref["tag"]["name"] == "AI" for ref in filtered)

    def test_filter_by_type_and_tag(self):
        """Test filtering by both type and tag."""
        refs = [
            {
                "bib_key": "ref1",
                "reference_type": "article",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 1),
            },
            {
                "bib_key": "ref2",
                "reference_type": "book",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 2),
            },
            {
                "bib_key": "ref3",
                "reference_type": "article",
                "tag": {"id": 2, "name": "ML"},
                "created_at": datetime(2024, 1, 3),
            },
            {
                "bib_key": "ref4",
                "reference_type": "article",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 4),
            },
        ]

        filtered = filter_and_sort_search_results(
            refs, ref_type_filter="article", tag_filter="AI"
        )

        assert len(filtered) == 2
        assert all(
            ref["reference_type"] == "article" and ref["tag"]["name"] == "AI"
            for ref in filtered
        )

    def test_sort_newest_first(self):
        """Test sorting by newest first."""
        refs = [
            {"bib_key": "ref1", "created_at": datetime(2024, 1, 1)},
            {"bib_key": "ref2", "created_at": datetime(2024, 3, 1)},
            {"bib_key": "ref3", "created_at": datetime(2024, 2, 1)},
        ]

        sorted_refs = filter_and_sort_search_results(refs, sort_by="newest")

        assert sorted_refs[0]["bib_key"] == "ref2"
        assert sorted_refs[1]["bib_key"] == "ref3"
        assert sorted_refs[2]["bib_key"] == "ref1"

    def test_sort_oldest_first(self):
        """Test sorting by oldest first."""
        refs = [
            {"bib_key": "ref1", "created_at": datetime(2024, 1, 1)},
            {"bib_key": "ref2", "created_at": datetime(2024, 3, 1)},
            {"bib_key": "ref3", "created_at": datetime(2024, 2, 1)},
        ]

        sorted_refs = filter_and_sort_search_results(refs, sort_by="oldest")

        assert sorted_refs[0]["bib_key"] == "ref1"
        assert sorted_refs[1]["bib_key"] == "ref3"
        assert sorted_refs[2]["bib_key"] == "ref2"

    def test_sort_by_title(self):
        """Test sorting by title."""
        refs = [
            {
                "bib_key": "ref1",
                "fields": {"title": "Zebra"},
                "created_at": datetime(2024, 1, 1),
            },
            {
                "bib_key": "ref2",
                "fields": {"title": "Apple"},
                "created_at": datetime(2024, 1, 2),
            },
        ]

        sorted_refs = filter_and_sort_search_results(refs, sort_by="title")

        assert sorted_refs[0]["fields"]["title"] == "Apple"
        assert sorted_refs[1]["fields"]["title"] == "Zebra"

    def test_filter_and_sort_combined(self):
        """Test filtering and sorting combined."""
        refs = [
            {
                "bib_key": "ref1",
                "reference_type": "article",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 1),
            },
            {
                "bib_key": "ref2",
                "reference_type": "article",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 3, 1),
            },
            {
                "bib_key": "ref3",
                "reference_type": "book",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 2, 1),
            },
            {
                "bib_key": "ref4",
                "reference_type": "article",
                "tag": {"id": 2, "name": "ML"},
                "created_at": datetime(2024, 4, 1),
            },
        ]

        filtered = filter_and_sort_search_results(
            refs, ref_type_filter="article", tag_filter="AI", sort_by="oldest"
        )

        assert len(filtered) == 2
        assert filtered[0]["bib_key"] == "ref1"
        assert filtered[1]["bib_key"] == "ref2"

    def test_empty_list(self):
        """Test with empty list."""
        result = filter_and_sort_search_results([])
        assert result == []

    def test_no_filters(self):
        """Test with no filters applied."""
        refs = [
            {"bib_key": "ref1", "created_at": datetime(2024, 1, 1)},
            {"bib_key": "ref2", "created_at": datetime(2024, 2, 1)},
        ]

        result = filter_and_sort_search_results(refs)

        assert len(result) == 2
        assert result[0]["bib_key"] == "ref2"

    def test_filter_no_matching_type(self):
        """Test filtering with no matching type."""
        refs = [
            {
                "bib_key": "ref1",
                "reference_type": "article",
                "created_at": datetime(2024, 1, 1),
            },
        ]

        filtered = filter_and_sort_search_results(refs, ref_type_filter="book")

        assert len(filtered) == 0

    def test_filter_no_matching_tag(self):
        """Test filtering with no matching tag."""
        refs = [
            {
                "bib_key": "ref1",
                "tag": {"id": 1, "name": "AI"},
                "created_at": datetime(2024, 1, 1),
            },
        ]

        filtered = filter_and_sort_search_results(refs, tag_filter="ML")

        assert len(filtered) == 0
