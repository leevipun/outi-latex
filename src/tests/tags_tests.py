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
