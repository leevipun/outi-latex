"""Tag management utilities."""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.config import db


class TagError(Exception):
    """Base exception for tag operations."""

    pass


class TagExistsError(Exception):
    """Raised when trying to add existing tag."""

    pass


def add_tag(tag: str):
    """Add a new tag to the database.

    Args:
        tag: The name of the tag to add (e.g., "machine-learning", "nlp").

    Returns:
        int: The ID of the newly created tag.

    Raises:
        TagExistsError: If a tag with this name already exists.
        TagError: If the database operation fails.
    """
    sql = text("INSERT INTO tags (name) VALUES (:tag) RETURNING id;")
    try:
        tag_id = db.session.execute(sql, {"tag": tag})
        db.session.commit()
        return tag_id.fetchone()[0]

    except IntegrityError as e:
        db.session.rollback()
        raise TagExistsError(f"Failed to add tag {tag}: {e}.")
    except Exception as e:
        db.session.rollback()
        raise TagError(f"Failed to add tag {tag}: {e}.")


def get_tags():
    """Fetch all tags from the database.

    Returns:
        list: List of dictionaries containing tag id and name,
              sorted alphabetically by name. Each dictionary has the format:
              {"id": int, "name": str}

    Raises:
        TagError: If the database query fails.
    """
    sql = text("SELECT id, name FROM tags ORDER BY name;")
    try:
        result = db.session.execute(sql)
        return [{"id": row[0], "name": row[1]} for row in result.fetchall()]

    except Exception as e:
        raise TagError(f"Failed to fetch tags: {e}.")


def get_tag_by_reference(reference_id: int):
    """Fetch the tag associated with a specific reference.

    Args:
        reference_id: The ID of the reference.

    Returns:
        dict or None: A dictionary containing tag id and name if found,
                      otherwise None. The dictionary has the format:
                      {"id": int, "name": str}

    Raises:
        TagError: If the database query fails.
    """
    sql = text(
        "SELECT t.id, t.name "
        "FROM tags t "
        "JOIN reference_tags rt ON t.id = rt.tag_id "
        "WHERE rt.reference_id = :reference_id;"
    )
    try:
        result = db.session.execute(sql, {"reference_id": reference_id})
        row = result.fetchone()
        if row:
            return {"id": row[0], "name": row[1]}
        return None

    except Exception as e:
        raise TagError(f"Failed to fetch tag for reference {reference_id}: {e}.")


def add_tag_to_reference(tag_id: int, reference_id: int):
    """Associate a tag with a reference, removing any existing tag associations first.

    This function replaces any existing tag for the reference with the new one.
    A reference can only have one tag at a time.

    Args:
        tag_id: The ID of the tag to associate with the reference.
        reference_id: The ID of the reference to tag.

    Raises:
        TagError: If the database operation fails.
    """
    try:
        delete_sql = text(
            "DELETE FROM reference_tags WHERE reference_id = :reference_id;"
        )
        db.session.execute(delete_sql, {"reference_id": reference_id})

        insert_sql = text(
            "INSERT INTO reference_tags (tag_id, reference_id) "
            "VALUES (:tag_id, :reference_id);"
        )
        db.session.execute(insert_sql, {"tag_id": tag_id, "reference_id": reference_id})
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise TagError(f"Failed to add tag {tag_id} to reference {reference_id}: {e}.")


def delete_tag_from_reference(reference_id: int):
    """Remove the tag association from a reference.

    Deletes all tag associations for the specified reference.

    Args:
        reference_id: The ID of the reference to remove tags from.

    Raises:
        TagError: If the database operation fails.
    """
    try:
        delete_sql = text(
            "DELETE FROM reference_tags WHERE reference_id = :reference_id;"
        )
        db.session.execute(delete_sql, {"reference_id": reference_id})
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise TagError(f"Failed to delete tag from reference {reference_id}: {e}.")
