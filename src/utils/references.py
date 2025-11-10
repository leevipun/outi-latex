"""Reference management utilities."""
from sqlalchemy import text

from config import db


def get_all_references() -> list:
    """Fetch all reference types from the database.

    Returns:
        list: List of dictionaries containing reference type id and name,
              sorted by id.
    """
    sql = text(
        """SELECT id, name 
             FROM reference_types 
             ORDER BY id;"""
    )
    reference_types = db.session.execute(sql)
    return [dict(row) for row in reference_types.mappings()]
