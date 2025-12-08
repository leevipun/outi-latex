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


def get_all_added_references(user_id: int | None = None) -> list:
    """Fetch all references added by a specific user or all public references."""
    try:
        if user_id is not None:
            sql_refs = text(
                """
                SELECT
                    sr.id,
                    sr.bib_key,
                    sr.is_public,
                    rt.name AS reference_type,
                    sr.created_at,
                    u.username,
                    ur.user_id as owner_id
                FROM single_reference sr
                JOIN user_ref ur ON ur.reference_id = sr.id AND ur.user_id = :user_id
                LEFT JOIN users u ON u.id = ur.user_id
                JOIN reference_types rt ON sr.reference_type_id = rt.id
                ORDER BY sr.created_at DESC
            """
            )
            params = {"user_id": user_id}
        else:
            sql_refs = text(
                """
                SELECT DISTINCT
                    sr.id,
                    sr.bib_key,
                    sr.is_public,
                    rt.name AS reference_type,
                    sr.created_at,
                    u.username,
                    ur.user_id as owner_id
                FROM single_reference sr
                JOIN user_ref ur ON ur.reference_id = sr.id
                LEFT JOIN users u ON u.id = ur.user_id
                JOIN reference_types rt ON sr.reference_type_id = rt.id
                WHERE sr.is_public = TRUE
                ORDER BY sr.created_at DESC
            """
            )
            params = {}

        results = db.session.execute(sql_refs, params)

        references = {}
        ref_ids = []
        for row in results.mappings():
            ref_id = row["id"]
            ref_ids.append(ref_id)
            references[ref_id] = {
                "bib_key": row["bib_key"],
                "is_public": row["is_public"],
                "reference_type": row["reference_type"],
                "created_at": row["created_at"],
                "username": row["username"],
                "owner_id": row["owner_id"],
                "fields": {},
                "tag": None,
            }

        if not ref_ids:
            return []

        # 2. Hae kaikki field values yhdellä kyselyllä
        sql_fields = text(
            """
            SELECT rv.reference_id, f.key_name, rv.value
            FROM reference_values rv
            JOIN fields f ON rv.field_id = f.id
            WHERE rv.reference_id IN :ref_ids
            ORDER BY rv.reference_id, f.key_name
        """
        )

        field_results = db.session.execute(sql_fields, {"ref_ids": tuple(ref_ids)})
        for row in field_results.mappings():
            ref_id = row["reference_id"]
            if ref_id in references:
                references[ref_id]["fields"][row["key_name"]] = row["value"]

        # 3. Hae tagit yhdellä kyselyllä
        sql_tags = text(
            """
            SELECT reftag.reference_id, t.id AS tag_id, t.name AS tag_name
            FROM reference_tags reftag
            JOIN tags t ON reftag.tag_id = t.id
            WHERE reftag.reference_id IN :ref_ids
        """
        )

        tag_results = db.session.execute(sql_tags, {"ref_ids": tuple(ref_ids)})
        for row in tag_results.mappings():
            ref_id = row["reference_id"]
            if ref_id in references:
                references[ref_id]["tag"] = {
                    "id": row["tag_id"],
                    "name": row["tag_name"],
                }

        return list(references.values())

    except Exception as e:
        raise DatabaseError(f"Failed to fetch added references: {e}")


def get_reference_by_bib_key(bib_key: str, user_id: int | None = None) -> dict:
    """Fetch a single reference by its bib_key for a specific user (if provided).

    Args:
        bib_key: The unique bib_key identifier for the reference.
        user_id: Optional user ID to filter by ownership (None = public only)

    Returns:
        dict: Dictionary containing bib_key, reference_type, created_at,
              username, is_public, and fields dictionary with all field values.
              Returns None if reference is not found.

    Raises:
        DatabaseError: If database query fails.
    """
    if user_id is not None:
        # Hae käyttäjän oma viite
        user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
        where_clause = "WHERE sr.bib_key = :bib_key AND ur.user_id = :user_id"
        params = {"bib_key": bib_key, "user_id": user_id}
    else:
        # Hae julkinen viite
        user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
        where_clause = "WHERE sr.bib_key = :bib_key AND sr.is_public = TRUE"
        params = {"bib_key": bib_key}

    sql = text(
        f"""SELECT
                sr.id,
                sr.bib_key,
                sr.is_public,
                rt.name AS reference_type,
                rt.id AS reference_type_id,
                sr.created_at,
                u.id AS owner_id,
                u.username,
                f.key_name,
                rv.value
            FROM single_reference sr
            {user_join}
            LEFT JOIN users u ON u.id = ur.user_id
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            {where_clause}
            ORDER BY f.key_name;"""
    )
    try:
        results = db.session.execute(sql, params)

        reference = None
        for row in results.mappings():
            if reference is None:
                reference = {
                    "id": row["id"],
                    "bib_key": row["bib_key"],
                    "is_public": row["is_public"],
                    "reference_type": row["reference_type"],
                    "reference_type_id": row["reference_type_id"],
                    "username": row["username"],
                    "created_at": row["created_at"],
                    "owner_id": row["owner_id"],
                    "fields": {},
                }

            # Add field value if it exists
            if row["key_name"] is not None:
                reference["fields"][row["key_name"]] = row["value"]

        return reference
    except Exception as e:
        raise DatabaseError(f"Failed to fetch reference by bib_key '{bib_key}': {e}")


def add_reference(reference_type_name: str, data: dict, editing: bool = False) -> int:
    """Lisää uusi viite tietokantaan tai päivitä olemassa oleva."""
    try:
        # 1) Hae viitetyypin id
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
        bib_key_to_check = old_bib_key if editing and old_bib_key else data["bib_key"]

        existing_ref = (
            db.session.execute(
                text("SELECT id FROM single_reference WHERE bib_key = :bib_key"),
                {"bib_key": bib_key_to_check},
            )
            .mappings()
            .first()
        )

        if "is_public" in data:
            is_public = data.pop("is_public")
        elif editing and existing_ref:
            # Muokataan olemassa olevaa viitettä, säilytetään nykyinen arvo
            current_visibility = db.session.execute(
                text("SELECT is_public FROM single_reference WHERE id = :ref_id"),
                {"ref_id": existing_ref["id"]},
            ).scalar()
            is_public = current_visibility if current_visibility is not None else True
        else:
            # Uusi viite, oletus on True (julkinen)
            is_public = True

        if existing_ref:
            if not editing:
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

            # Päivitä bib_key JA is_public jos ne muuttuivat
            if old_bib_key and data["bib_key"] != old_bib_key:
                db.session.execute(
                    text(
                        """UPDATE single_reference
                           SET bib_key = :new_bib_key, is_public = :is_public
                           WHERE id = :id"""
                    ),
                    {
                        "new_bib_key": data["bib_key"],
                        "is_public": is_public,
                        "id": ref_id,
                    },
                )
            else:
                # Päivitä vain is_public (bib_key pysyy samana)
                db.session.execute(
                    text(
                        """UPDATE single_reference
                           SET is_public = :is_public
                           WHERE id = :id"""
                    ),
                    {"is_public": is_public, "id": ref_id},
                )
        else:
            # Luodaan uusi viite
            insert_ref = db.session.execute(
                text(
                    """
                    INSERT INTO single_reference (bib_key, reference_type_id, is_public)
                    VALUES (:bib_key, :reference_type_id, :is_public)
                    RETURNING id;
                    """
                ),
                {
                    "bib_key": data["bib_key"],
                    "reference_type_id": reference_type_id,
                    "is_public": is_public,
                },
            )
            db.session.flush()

            ref_id = insert_ref.scalar()
            if ref_id is None:
                row = insert_ref.mappings().first()
                ref_id = row["id"]

        # 3) Lisää kentät reference_values-tauluun
        for key, value in data.items():
            if key in ("bib_key", "old_bib_key"):
                continue
            if value in (None, ""):
                continue

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

            if field_row is None:
                continue

            field_id = field_row["id"]

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

    except Exception as exc:
        db.session.rollback()
        raise DatabaseError(f"Failed to insert/update reference: {exc}") from exc


def delete_reference_by_bib_key(bib_key: str, user_id: int | None = None) -> None:
    """Delete a reference (and its values via cascade) by bib_key.

    Args:
        bib_key: The BibTeX key of the reference to delete.
        user_id: Optional user id to enforce ownership.

    Raises:
        DatabaseError: If the delete operation fails.
    """
    try:
        if user_id is None:
            db.session.execute(
                text("DELETE FROM single_reference WHERE bib_key = :bib_key"),
                {"bib_key": bib_key},
            )
        else:
            db.session.execute(
                text(
                    """
                    DELETE FROM single_reference sr
                    USING user_ref ur
                    WHERE sr.bib_key = :bib_key
                      AND ur.reference_id = sr.id
                      AND ur.user_id = :user_id
                    """
                ),
                {"bib_key": bib_key, "user_id": user_id},
            )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to delete reference '{bib_key}': {e}") from e


def search_reference_by_query(query: str, user_id: int | None = None) -> list:
    """Search for references matching the given query string."""
    try:
        if user_id is not None:
            user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
            where_clause = "WHERE sr.is_public = TRUE"
            params = {"query": f"%{query}%", "user_id": user_id}
        else:
            user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
            where_clause = "WHERE sr.is_public = TRUE"
            params = {"query": f"%{query}%"}

        sql = text(
            f"""
            SELECT
                sr.id,
                sr.bib_key,
                sr.is_public,
                rt.name AS reference_type,
                sr.created_at,
                f.key_name,
                rv.value,
                t.id AS tag_id,
                t.name AS tag_name,
                u.username AS username,
                ur.user_id as owner_id
            FROM single_reference sr
            {user_join}
            LEFT JOIN users u ON u.id = ur.user_id
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            LEFT JOIN reference_tags reftag ON sr.id = reftag.reference_id
            LEFT JOIN tags t ON reftag.tag_id = t.id
            {where_clause}
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
        results = db.session.execute(sql, params)

        references = {}
        for row in results.mappings():
            ref_id = row["id"]
            if ref_id not in references:
                references[ref_id] = {
                    "bib_key": row["bib_key"],
                    "is_public": row["is_public"],
                    "reference_type": row["reference_type"],
                    "created_at": row["created_at"],
                    "username": row["username"],
                    "owner_id": row["owner_id"],
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
    ref_type_filter: str = "",
    tag_filter: str = "",
    sort_by: str = "newest",
    user_id: int | None = None,
) -> list:
    try:
        if user_id is not None:
            user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
            params = {"user_id": user_id}
        else:
            # VAIN julkiset viitteet (kaikki käyttäjät)
            user_join = "JOIN user_ref ur ON ur.reference_id = sr.id"
            params = {}

        base_sql = f"""
            SELECT DISTINCT
                sr.id,
                sr.bib_key,
                rt.name AS reference_type,
                sr.created_at,
                f.key_name,
                rv.value,
                t.id AS tag_id,
                t.name AS tag_name,
                ur.user_id as owner_id
            FROM single_reference sr
            {user_join}
            JOIN reference_types rt ON sr.reference_type_id = rt.id
            LEFT JOIN reference_values rv ON sr.id = rv.reference_id
            LEFT JOIN fields f ON rv.field_id = f.id
            LEFT JOIN reference_tags reftag ON sr.id = reftag.reference_id
            LEFT JOIN tags t ON reftag.tag_id = t.id
            WHERE sr.is_public = TRUE
        """

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
                    "owner_id": row["owner_id"],
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


def get_reference_visibility(bib_key: str) -> bool:
    """Get the is_public status of a reference."""
    try:
        sql = text("SELECT is_public FROM single_reference WHERE bib_key = :bib_key")
        result = db.session.execute(sql, {"bib_key": bib_key}).mappings().first()

        if result:
            return result["is_public"]

        return True

    except Exception as e:
        raise DatabaseError(f"Failed to fetch visibility for '{bib_key}': {e}") from e
