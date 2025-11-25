"""Reference management utilities."""

from sqlalchemy import text

from src.config import db


class ReferenceError(Exception):
    """Base exception for reference operations."""

    pass


class DatabaseError(ReferenceError):
    """Raised when database query fails."""

    pass


def get_all_references() -> list:
    """Fetch all reference types from the database.

    Returns:
        list: List of dictionaries containing reference type id and name,
              sorted by id.

    Raises:
        DatabaseError: If database query fails.
    """
    sql = text(
        """SELECT id, name 
             FROM reference_types 
             ORDER BY id;"""
    )
    try:
        reference_types = db.session.execute(sql)
        return [dict(row) for row in reference_types.mappings()]
    except Exception as e:
        raise DatabaseError(f"Failed to fetch reference types: {e}")


def get_all_added_references() -> list:
    """Fetch all added reference from the database with all their field values.

    Returns:
        list: List of dictionaries containing bib-key, reference type,
              timestamp, and all field values, sorted by timestamp.

    Raises:
        DatabaseError: If database query fails.
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
    try:
        results = db.session.execute(sql)

        # Group results by reference
        references = {}
        for row in results.mappings():
            ref_id = row["id"]
            if ref_id not in references:
                references[ref_id] = {
                    "bib_key": row["bib_key"],
                    "reference_type": row["reference_type"],
                    "created_at": row["created_at"],
                    "fields": {},
                }

            # Add field value if it exists
            if row["key_name"] is not None:
                references[ref_id]["fields"][row["key_name"]] = row["value"]

        return list(references.values())
    except Exception as e:
        raise DatabaseError(f"Failed to fetch added references: {e}")


def get_reference_by_bib_key(bib_key: str) -> dict:
    """Fetch a single reference by its bib_key.

    Args:
        bib_key: The unique bib_key identifier for the reference.

    Returns:
        dict: Dictionary containing bib_key, reference_type, created_at,
              and fields dictionary with all field values.
              Returns None if reference is not found.

    Raises:
        DatabaseError: If database query fails.
    """
    sql = text(
        """ SELECT 
                sr.id,
                sr.bib_key,
                rt.name AS reference_type,
                sr.reference_type_id,
                sr.created_at,
                f.key_name,
                rv.value
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            WHERE sr.bib_key = :bib_key
            ORDER BY f.key_name;"""
    )
    try:
        results = db.session.execute(sql, {"bib_key": bib_key})

        reference = None
        for row in results.mappings():
            if reference is None:
                reference = {
                    "id": row["id"],
                    "bib_key": row["bib_key"],
                    "reference_type": row["reference_type"],
                    "reference_type_id": row["reference_type_id"],
                    "created_at": row["created_at"],
                    "fields": {},
                }

            # Add field value if it exists
            if row["key_name"] is not None:
                reference["fields"][row["key_name"]] = row["value"]

        return reference
    except Exception as e:
        raise DatabaseError(f"Failed to fetch reference by bib_key '{bib_key}': {e}")


def add_reference(reference_type_name: str, data: dict) -> None:
    """Lisää uusi viite tietokantaan tai päivitä olemassa oleva.

    Jos bib_key on jo olemassa, päivitetään sen kentät.
    Oletus: Viitetyyppi ei muutu, mutta kentät voivat muuttua.

    Args:
        reference_type_name: viitetyypin nimi, esim. "article" (tulee lomakkeelta / URL:sta)
        data: lomakedata dictinä, esim:
              {
                  "bib_key": "Martin2009",
                  "author": "Martin, O.",
                  "title": "Nice paper",
                  "year": "2009",
                  ...
              }

    Raises:
        DatabaseError: jos tietokantaoperaatio epäonnistuu.
    """
    try:
        # 1) Hae viitetyypin id reference_types-taulusta
        result = (
            db.session.execute(
                text("SELECT id FROM reference_types WHERE name = :name"),
                {"name": reference_type_name},
            )
            .mappings()
            .first()
        )

        if result is None:
            raise DatabaseError(f"Unknown reference type: {reference_type_name}")

        reference_type_id = result["id"]

        # 2) Tarkista onko viite jo olemassa
        old_bib_key = (
            data.get("old_bib_key", "").strip()
            if isinstance(data.get("old_bib_key"), str)
            else None
        )
        bib_key_to_check = old_bib_key if old_bib_key else data["bib_key"]

        existing_ref = (
            db.session.execute(
                text("SELECT id FROM single_reference WHERE bib_key = :bib_key"),
                {"bib_key": bib_key_to_check},
            )
            .mappings()
            .first()
        )

        if existing_ref:
            # Viite on jo olemassa, päivitetään kentät
            ref_id = existing_ref["id"]

            # Poistetaan vanhat kentät
            db.session.execute(
                text("DELETE FROM reference_values WHERE reference_id = :reference_id"),
                {"reference_id": ref_id},
            )
            db.session.flush()

            db.session.execute(
                text(
                    "UPDATE single_reference SET bib_key = :new_bib_key WHERE id = :id"
                ),
                {"new_bib_key": data["bib_key"], "id": ref_id},
            )
        else:
            # Luodaan uusi viite
            insert_ref = db.session.execute(
                text(
                    """
                    INSERT INTO single_reference (bib_key, reference_type_id)
                    VALUES (:bib_key, :reference_type_id)
                    RETURNING id;
                    """
                ),
                {
                    "bib_key": data["bib_key"],
                    "reference_type_id": reference_type_id,
                },
            )
            db.session.flush()

            # .scalar() toimii useimmissa, mutta jos ei, käytetään mappings().first()
            ref_id = insert_ref.scalar()
            if ref_id is None:
                row = insert_ref.mappings().first()
                ref_id = row["id"]

        # 3) Jokaiselle kentälle (paitsi bib_key ja old_bib_key) lisätään rivi reference_values-tauluun
        for key, value in data.items():
            print(key, value)  # --- DEBUG ---
            if key in ("bib_key", "old_bib_key"):
                continue
            if value in (None, ""):
                continue  # ei tallenneta tyhjiä

            # Hae field_id fields-taulusta (key_name + reference_type_id)
            field_row = (
                db.session.execute(
                    text(
                        """
                    SELECT f.id
                    FROM fields f
                    JOIN reference_type_fields rtf ON rtf.field_id = f.id
                    WHERE f.key_name = :key_name
                    AND rtf.reference_type_id = :reference_type_id;
                    """
                    ),
                    {
                        "key_name": key,
                        "reference_type_id": reference_type_id,
                    },
                )
                .mappings()
                .first()
            )

            # Jos kenttää ei löydy skeemasta, skippaa (voi myös nostaa virheen jos haluat)
            if field_row is None:
                continue

            field_id = field_row["id"]

            # Lisää arvo reference_values-tauluun
            db.session.execute(
                text(
                    """
                    INSERT INTO reference_values (reference_id, field_id, value)
                    VALUES (:reference_id, :field_id, :value);
                    """
                ),
                {
                    "reference_id": ref_id,
                    "field_id": field_id,
                    "value": value,
                },
            )

        db.session.commit()

    except Exception as exc:  # voit tiukentaa myöhemmin
        db.session.rollback()
        raise DatabaseError(f"Failed to insert reference: {exc}") from exc


def delete_reference_by_bib_key(bib_key: str) -> None:
    """Delete a reference (and its values via cascade) by bib_key.

    Args:
        bib_key: The BibTeX key of the reference to delete.

    Raises:
        DatabaseError: If the delete operation fails.
    """
    try:
        db.session.execute(
            text("DELETE FROM single_reference WHERE bib_key = :bib_key"),
            {"bib_key": bib_key},
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to delete reference '{bib_key}': {e}") from e


def search_reference_by_query(query: str) -> list:
    """Search for references matching the given query string.

    Searches across bib_key, author, title, and other field values.

    Args:
        query: The search query string.

    Returns:
        list: List of dictionaries containing matching references with their fields.

    Raises:
        DatabaseError: If the search query fails.
    """
    try:
        sql = text(
            """
            SELECT DISTINCT
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
            WHERE sr.bib_key LIKE :query
               OR rv.value LIKE :query
            ORDER BY sr.created_at DESC, sr.id, f.key_name;
            """
        )
        results = db.session.execute(sql, {"query": f"%{query}%"})
        references = {}
        for row in results.mappings():
            ref_id = row["id"]
            if ref_id not in references:
                references[ref_id] = {
                    "bib_key": row["bib_key"],
                    "reference_type": row["reference_type"],
                    "created_at": row["created_at"],
                    "fields": {},
                }

            # Add field value if it exists
            if row["key_name"] is not None:
                references[ref_id]["fields"][row["key_name"]] = row["value"]

        return list(references.values())
    except Exception as e:
        raise DatabaseError(
            f"Failed to search references with query '{query}': {e}"
        ) from e
