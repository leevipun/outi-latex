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
    """Fetch all PUBLIC added references from the database with all their field values and tags.

    Returns:
        list: List of dictionaries containing bib-key, reference type,
              timestamp, all field values, and associated tag, sorted by timestamp.
              Only returns references where is_public = TRUE.

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
                rv.value,
                t.id AS tag_id,
                t.name AS tag_name
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            LEFT JOIN reference_tags reftag ON sr.id = reftag.reference_id
            LEFT JOIN tags t ON reftag.tag_id = t.id
            WHERE sr.is_public = TRUE
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
                    "tag": None,
                }

                # Add tag if it exists
                if row["tag_id"] is not None:
                    references[ref_id]["tag"] = {
                        "id": row["tag_id"],
                        "name": row["tag_name"],
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


def add_reference(reference_type_name: str, data: dict, editing: bool = False) -> int:
    """Lisää uusi viite tietokantaan tai päivitä olemassa oleva.

    Jos editing=True ja bib_key on jo olemassa, päivitetään sen kentät.
    Jos editing=False ja bib_key on jo olemassa, heitetään virhe.
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
        editing: True jos muokataan olemassa olevaa viitettä, False jos lisätään uusi

    Returns:
        int: Lisätyn tai päivitetyn viitteen id.

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
        # Kun muokataan, käytetään vanhaa avainta löytämiseen
        bib_key_to_check = old_bib_key if editing and old_bib_key else data["bib_key"]

        existing_ref = (
            db.session.execute(
                text("SELECT id FROM single_reference WHERE bib_key = :bib_key"),
                {"bib_key": bib_key_to_check},
            )
            .mappings()
            .first()
        )

        if existing_ref:
            if not editing:
                # Yritettiin lisätä uusi viite, mutta se on jo olemassa
                raise DatabaseError(
                    f"Reference with bib_key '{bib_key_to_check}' already exists. "
                    "Use edit mode to update it."
                )

            # Muokataan olemassa olevaa viitettä
            ref_id = existing_ref["id"]

            # Poistetaan vanhat kentät
            db.session.execute(
                text("DELETE FROM reference_values WHERE reference_id = :reference_id"),
                {"reference_id": ref_id},
            )
            db.session.flush()

            # Päivitä bib_key jos se muuttui
            if old_bib_key and data["bib_key"] != old_bib_key:
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
        return ref_id

    except Exception as exc:  # voit tiukentaa myöhemmin
        db.session.rollback()
        raise DatabaseError(f"Failed to insert/update reference: {exc}") from exc


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
    """Search for PUBLIC references matching the given query string.

    Searches across bib_key, author, title, and other field values.
    Only returns public references.

    Args:
        query: The search query string.

    Returns:
        list: List of dictionaries containing matching public references with their fields and tags.

    Raises:
        DatabaseError: If the search query fails.
    """
    try:
        sql = text(
            """
            SELECT
                sr.id,
                sr.bib_key,
                rt.name AS reference_type,
                sr.created_at,
                f.key_name,
                rv.value,
                t.id AS tag_id,
                t.name AS tag_name
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            LEFT JOIN reference_tags reftag ON sr.id = reftag.reference_id
            LEFT JOIN tags t ON reftag.tag_id = t.id
            WHERE sr.is_public = TRUE
              AND sr.id IN (
                SELECT DISTINCT sr2.id
                FROM single_reference sr2
                LEFT JOIN reference_values rv2 ON sr2.id = rv2.reference_id
                WHERE sr2.bib_key LIKE :query
                   OR rv2.value LIKE :query
            )
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
                    "tag": None,
                }

                if row["tag_id"] is not None:
                    references[ref_id]["tag"] = {
                        "id": row["tag_id"],
                        "name": row["tag_name"],
                    }

            if row["key_name"] is not None:
                references[ref_id]["fields"][row["key_name"]] = row["value"]

        return list(references.values())
    except Exception as e:
        raise DatabaseError(
            f"Failed to search references with query '{query}': {e}"
        ) from e


def sort_references_by_created_at(references: list, sort_type: str = "newest") -> list:
    """Sort references by creation date.

    Args:
        references: List of reference dictionaries
        sort_type: "newest" (desc) or "oldest" (asc)

    Returns:
        list: Sorted references
    """
    if not references:
        return []

    def get_created_at(ref):
        created_at = ref.get("created_at")
        if hasattr(created_at, "isoformat"):
            return created_at.isoformat()
        return created_at or ""

    reverse = sort_type == "newest"
    try:
        return sorted(references, key=get_created_at, reverse=reverse)
    except Exception as e:
        print(f"Warning: Date sorting failed: {e}")
        return references


def sort_references_by_field(
    references: list, sort_by: str, sort_order: str = "asc"
) -> list:
    """Sort references by a field value (title, author, etc.).

    Args:
        references: List of reference dictionaries
        sort_by: Field name to sort by ("title", "author")
        sort_order: "asc" or "desc"

    Returns:
        list: Sorted references
    """

    def get_sort_value(ref):
        value = ref.get("fields", {}).get(sort_by, "")

        cleaned = str(value).lower().strip()

        for article in ["the ", "a ", "an "]:
            if cleaned.startswith(article):
                cleaned = cleaned[len(article) :].strip()
                break

        return cleaned

    reverse = sort_order == "desc"
    return sorted(references, key=get_sort_value, reverse=reverse)


def sort_references_by_bib_key(references: list, sort_order: str = "asc") -> list:
    """Sort references by bib_key alphabetically.

    Args:
        references: List of reference dictionaries
        sort_order: "asc" or "desc"

    Returns:
        list: Sorted references
    """

    def get_bib_key(ref):
        bib_key = ref.get("bib_key", "")
        return str(bib_key).lower().strip()

    reverse = sort_order == "desc"
    try:
        return sorted(references, key=get_bib_key, reverse=reverse)
    except Exception as e:
        print(f"Warning: Bib key sorting failed: {e}")
        return references


def get_references_filtered_sorted(
    ref_type_filter: str = "", tag_filter: str = "", sort_by: str = "newest"
) -> list:
    try:
        base_sql = """
            SELECT DISTINCT
                sr.id,
                sr.bib_key,
                rt.name AS reference_type,
                sr.created_at,
                f.key_name,
                rv.value,
                t.id AS tag_id,
                t.name AS tag_name
            FROM single_reference sr
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            LEFT JOIN reference_tags reftag ON sr.id = reftag.reference_id
            LEFT JOIN tags t ON reftag.tag_id = t.id
            WHERE sr.is_public = TRUE
        """

        params = {}
        conditions = []

        if ref_type_filter.strip():
            conditions.append("rt.name = :ref_type")
            params["ref_type"] = ref_type_filter.strip()

        if tag_filter.strip():
            conditions.append("t.name = :tag_name")
            params["tag_name"] = tag_filter.strip()

        if conditions:
            base_sql += " AND " + " AND ".join(conditions)

        if sort_by == "oldest":
            order_clause = "ORDER BY sr.created_at ASC, sr.id, f.key_name"
        elif sort_by == "bib_key":
            order_clause = "ORDER BY sr.bib_key ASC, sr.id, f.key_name"
        else:
            order_clause = "ORDER BY sr.created_at DESC, sr.id, f.key_name"

        base_sql += " " + order_clause

        results = db.session.execute(text(base_sql), params)

        references = {}
        for row in results.mappings():
            ref_id = row["id"]
            if ref_id not in references:
                references[ref_id] = {
                    "id": ref_id,
                    "bib_key": row["bib_key"],
                    "reference_type": row["reference_type"],
                    "created_at": row["created_at"],
                    "fields": {},
                    "tag": None,
                }

            if row["tag_id"] is not None:
                references[ref_id]["tag"] = {
                    "id": row["tag_id"],
                    "name": row["tag_name"],
                }

            if row["key_name"] and row["value"]:
                references[ref_id]["fields"][row["key_name"]] = row["value"]

        reference_list = list(references.values())

        if sort_by == "title":
            reference_list = sort_references_by_field(reference_list, "title", "asc")
        elif sort_by == "author":
            reference_list = sort_references_by_field(reference_list, "author", "asc")
        return reference_list

    except Exception as e:
        raise DatabaseError(f"Failed to fetch filtered references: {e}") from e


def filter_and_sort_search_results(
    search_results: list,
    ref_type_filter: str = "",
    tag_filter: str = "",
    sort_by: str = "newest",
) -> list:
    """Apply filters and sorting to existing search results.

    Args:
        search_results: Results from search_reference_by_query()
        ref_type_filter: Filter by reference type
        tag_filter: Filter by tag name
        sort_by: Sort type - "newest", "oldest", "title", "author", "bib_key"

    Returns:
        list: Filtered and sorted results
    """
    if not search_results:
        return []

    filtered = search_results.copy()

    if ref_type_filter.strip():
        filtered = [
            ref for ref in filtered if ref.get("reference_type") == ref_type_filter
        ]

    if tag_filter.strip():
        filtered = [
            ref
            for ref in filtered
            if ref.get("tag") is not None
            and isinstance(ref.get("tag"), dict)
            and ref["tag"].get("name") == tag_filter
        ]

    try:
        if sort_by in ["newest", "oldest"]:
            sorted_results = sort_references_by_created_at(filtered, sort_by)
        elif sort_by in ["title", "author"]:
            sorted_results = sort_references_by_field(filtered, sort_by, "asc")
        elif sort_by == "bib_key":
            sorted_results = sort_references_by_bib_key(filtered, "asc")
        else:
            sorted_results = sort_references_by_created_at(filtered, "newest")

        return sorted_results
    except Exception as e:
        print(f"Warning: Sorting failed, returning filtered results: {e}")
        return filtered
