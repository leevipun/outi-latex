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
    """Fetch all added reference from the database with all their field values.

    Returns:
        list: List of dictionaries containing bib-key, reference type,
              timestamp, and all field values, sorted by timestamp.
    """
    sql = text(
        """ SELECT 
                sr.id,
                sr.bib_key,
                rt.name AS reference_type,
                sr.created_at,
                f.key_name,
                rv.value
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            ORDER BY sr.created_at DESC, sr.id, f.key_name;"""
    )
    results = db.session.execute(sql)
    
    # Group results by reference
    references = {}
    for row in results.mappings():
        ref_id = row['id']
        if ref_id not in references:
            references[ref_id] = {
                'bib_key': row['bib_key'],
                'reference_type': row['reference_type'],
                'created_at': row['created_at'],
                'fields': {}
            }
        
        # Add field value if it exists
        if row['key_name'] is not None:
            references[ref_id]['fields'][row['key_name']] = row['value']
    
    return list(references.values())
