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


def get_all_added_references() -> list:
    """Fetch all added reference from the database.

    Returns:
        list: List of dictionaries containing bib-key, reference type and
              timestamp, sorted by timestamp.
    """
    sql = text(
        """ SELECT 
                sr.bib_key,
                rt.name AS reference_type,
                sr.created_at
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            ORDER BY sr.created_at DESC;"""
    )
    reference_types = db.session.execute(sql)
    return [dict(row) for row in reference_types.mappings()]
