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


def add_tag(tag:str):
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
    sql = text("SELECT id, name FROM tags ORDER BY name;")
    try:
        result = db.session.execute(sql)
        return [{"id": row[0], "name": row[1]} for row in result.fetchall()]

    except Exception as e:
        raise TagError(f"Failed to fetch tags: {e}.")


def add_tag_to_reference(tag_id:int, reference_id:int):
    try:
        delete_sql = text(
            "DELETE FROM reference_tags WHERE reference_id = :reference_id;"
        )
        db.session.execute(delete_sql, {"reference_id": reference_id})

        insert_sql = text(
            "INSERT INTO reference_tags (tag_id, reference_id) "
            "VALUES (:tag_id, :reference_id);"
        )
        db.session.execute(
            insert_sql, {"tag_id": tag_id, "reference_id": reference_id}
        )
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise TagError(
            f"Failed to add tag {tag_id} to reference {reference_id}: {e}."
        )

def delete_tag_from_reference(reference_id:int):
    try:
        delete_sql = text(
            "DELETE FROM reference_tags WHERE reference_id = :reference_id;"
        )
        db.session.execute(delete_sql, {"reference_id": reference_id})
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise TagError(
            f"Failed to delete tag from reference {reference_id}: {e}."
        )
