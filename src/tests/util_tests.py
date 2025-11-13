"""Unit tests for src/util.py utility functions."""

import json
from unittest.mock import mock_open, patch

import pytest

from src.util import (
    get_fields_for_type,
    get_reference_type_by_id,
    load_form_fields,
)


@pytest.fixture
def sample_form_fields():
    """Fixture providing sample form fields data."""
    return {
        "article": [
            {
                "key": "author",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "title",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "journal",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "year",
                "input-type": "number",
                "type": "int",
                "required": True,
                "additional": False,
            },
            {
                "key": "volume",
                "input-type": "number",
                "type": "int",
                "required": False,
                "additional": False,
            },
        ],
        "book": [
            {
                "key": "author/editor",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "title",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "publisher",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "year",
                "input-type": "number",
                "type": "int",
                "required": True,
                "additional": False,
            },
        ],
        "inproceedings": [
            {
                "key": "author",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "title",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "booktitle",
                "input-type": "text",
                "type": "str",
                "required": True,
                "additional": False,
            },
            {
                "key": "year",
                "input-type": "number",
                "type": "int",
                "required": True,
                "additional": False,
            },
        ],
    }


class TestGetReferenceTypeById:
    """Tests for get_reference_type_by_id function."""

    REFERENCE_TYPES = [
        {"id": 1, "name": "article"},
        {"id": 2, "name": "book"},
        {"id": 3, "name": "inproceedings"},
    ]

    def test_with_dict_reference_types(self):
        """Test finding reference type by ID with dictionary objects."""
        result = get_reference_type_by_id(1, self.REFERENCE_TYPES)
        assert result == "article"

    def test_with_dict_reference_types_middle_value(self):
        """Test finding reference type by ID with middle value."""
        result = get_reference_type_by_id(2, self.REFERENCE_TYPES)
        assert result == "book"

    def test_with_dict_reference_types_last_value(self):
        """Test finding reference type by ID with last value."""
        result = get_reference_type_by_id(3, self.REFERENCE_TYPES)
        assert result == "inproceedings"

    def test_id_not_found_returns_none(self):
        """Test that None is returned when ID is not found."""
        reference_types = [
            {"id": 1, "name": "article"},
            {"id": 2, "name": "book"},
        ]
        result = get_reference_type_by_id(999, reference_types)
        assert result is None

    def test_empty_reference_types_returns_none(self):
        """Test that None is returned for empty reference types."""
        result = get_reference_type_by_id(1, [])
        assert result is None

    def test_with_missing_id_field_returns_none(self):
        """Test handling of malformed dictionary without id field."""
        reference_types = [
            {"name": "article"},  # Missing id
            {"id": 2, "name": "book"},
        ]
        result = get_reference_type_by_id(1, reference_types)
        assert result is None

    def test_with_missing_name_field(self):
        """Test handling of dictionary missing name field."""
        reference_types = [
            {"id": 1},  # Missing name
            {"id": 2, "name": "book"},
        ]
        result = get_reference_type_by_id(1, reference_types)
        assert result is None

    def test_handles_key_error_exception(self):
        """Test that function handles KeyError gracefully."""
        reference_types = [None, {"id": 1, "name": "article"}]
        result = get_reference_type_by_id(1, reference_types)
        # Should not crash and should find the valid entry
        assert result == "article"

    def test_with_zero_id(self):
        """Test finding reference type with ID 0."""
        reference_types = [
            {"id": 0, "name": "unknown"},
            {"id": 1, "name": "article"},
        ]
        result = get_reference_type_by_id(0, reference_types)
        assert result == "unknown"

    def test_with_negative_id(self):
        """Test finding reference type with negative ID."""
        reference_types = [
            {"id": -1, "name": "invalid"},
            {"id": 1, "name": "article"},
        ]
        result = get_reference_type_by_id(-1, reference_types)
        assert result == "invalid"


class TestGetFieldsForType:
    """Tests for get_fields_for_type function."""

    def test_get_fields_for_article(self, sample_form_fields):
        """Test getting fields for article type."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_fields_for_book(self, sample_form_fields):
        """Test getting fields for book type."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("book")
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_fields_for_nonexistent_type(self, sample_form_fields):
        """Test getting fields for non-existent type returns empty list."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("nonexistent_type")
            assert result == []

    def test_article_fields_contain_required_keys(self, sample_form_fields):
        """Test that article fields have required structure."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            for field in result:
                assert "key" in field
                assert "input-type" in field
                assert "type" in field
                assert "required" in field
                assert "additional" in field

    def test_article_required_fields(self, sample_form_fields):
        """Test that article has correct required fields."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            required_keys = [f["key"] for f in result if f["required"]]
            expected_required = {"author", "title", "journal", "year"}
            assert expected_required.issubset(set(required_keys))

    def test_article_optional_fields(self, sample_form_fields):
        """Test that article has optional fields."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            optional_keys = [f["key"] for f in result if not f["required"]]
            assert len(optional_keys) > 0

    def test_case_sensitive_type_name(self, sample_form_fields):
        """Test that type name is case-sensitive."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result_lower = get_fields_for_type("article")
            result_upper = get_fields_for_type("ARTICLE")
            assert len(result_lower) > 0
            assert result_upper == []

    def test_book_type_fields(self, sample_form_fields):
        """Test specific structure of book type fields."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("book")
            keys = [f["key"] for f in result]
            assert "author/editor" in keys
            assert "title" in keys
            assert "publisher" in keys
            assert "year" in keys

    def test_inproceedings_type_fields(self, sample_form_fields):
        """Test specific structure of inproceedings type fields."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("inproceedings")
            keys = [f["key"] for f in result]
            assert "author" in keys
            assert "title" in keys
            assert "booktitle" in keys
            assert "year" in keys

    def test_fields_have_correct_input_types(self, sample_form_fields):
        """Test that fields have valid input types."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            valid_input_types = {"text", "number"}
            for field in result:
                assert field["input-type"] in valid_input_types

    def test_fields_have_correct_python_types(self, sample_form_fields):
        """Test that fields have valid Python type specifications."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            result = get_fields_for_type("article")
            valid_types = {"str", "int"}
            for field in result:
                assert field["type"] in valid_types


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_workflow_get_type_then_fields(self, sample_form_fields):
        """Test workflow of getting type then getting fields for that type."""
        reference_types = [
            {"id": 1, "name": "article"},
            {"id": 2, "name": "book"},
        ]

        # Get the type name
        type_name = get_reference_type_by_id(1, reference_types)
        assert type_name is not None

        # Get fields for that type
        with patch("util.load_form_fields", return_value=sample_form_fields):
            fields = get_fields_for_type(type_name)
            assert len(fields) > 0
            assert all("key" in f for f in fields)

    def test_all_form_field_types_are_accessible(self, sample_form_fields):
        """Test that all types in sample form fields are accessible."""
        with patch("util.load_form_fields", return_value=sample_form_fields):
            for type_name in sample_form_fields.keys():
                fields = get_fields_for_type(type_name)
                assert len(fields) > 0
                assert fields == sample_form_fields[type_name]


class TestLoadFormFieldsWithMocking:
    """Tests for load_form_fields function using mocks."""

    def test_load_form_fields_returns_dict(self, sample_form_fields):
        """Test that load_form_fields returns a dictionary."""
        with patch(
            "builtins.open", mock_open(read_data=json.dumps(sample_form_fields))
        ):
            result = load_form_fields()
            assert isinstance(result, dict)

    def test_load_form_fields_file_not_found(self):
        """Test load_form_fields handles missing file gracefully."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                load_form_fields()

    def test_load_form_fields_invalid_json(self):
        """Test load_form_fields handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                load_form_fields()
