"""Tag management utilities."""

from sqlalchemy import text

from src.config import db


class TagError(Exception):
    """Base exception for tag operations."""

    pass


def add_tags():
    ...


def get_tags():
    ...
