"""Tag management utilities."""

from sqlalchemy import text

from src.config import db


class TagError(Exception):
    """Base exception for tag operations."""

    pass


class TagExistsError(Exception):
    """Raised when trying to add existing tag."""

    pass


def add_tag(tag:str):
    sql = text(
        """ INSERT INTO tags (name)
            VALUES (:tag);
        """
    )
    try:
        db.session.execute(sql, {"tag": tag})
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise TagExistsError(f"Failed to add tag {tag}: {e}.")


def get_tags():
    sql = text(
        "SELECT id, name FROM tags ORDER BY name;"
    )
    try:
        result = db.session.execute(sql)
        return [{"id": row[0], "name": row[1]} for row in result.fetchall()]

    except Exception as e:
        raise TagError(f"Failed to fetch tags: {e}.")
