"""User management utilities."""

from sqlalchemy import text

from src.config import db


class UserError(Exception):
    """Base exception for user operations."""

    pass


def get_user_by_username(username):
    # TODO
    raise NotImplementedError("Not implemented yet")
