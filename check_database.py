#!/usr/bin/env python3
"""
Database inspection script - view what's in your database.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


def print_header(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    engine = create_engine(database_url)
    print("Connected to database\n")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {', '.join(tables)}\n")

    with Session(engine) as session:
        # 1. Reference Types
        print_header("REFERENCE TYPES")
        try:
            result = session.execute(
                text("SELECT id, name FROM reference_types ORDER BY id")
            )
            types = result.fetchall()
            if types:
                for id_, name in types:
                    print(f"  {id_}: {name}")
            else:
                print("  (No reference types)")
        except Exception as e:
            print(f"  (Error reading reference_types: {e})")
            types = []
        print()

        # 2. Fields
        print_header("FIELDS")
        try:
            result = session.execute(
                text(
                    """
                    SELECT id, key_name, data_type, input_type, additional
                    FROM fields
                    ORDER BY id
                    """
                )
            )
            fields = result.fetchall()
            if fields:
                for id_, key_name, data_type, input_type, additional in fields:
                    additional_str = " [ADDITIONAL]" if additional else ""
                    print(
                        f"  {id_}: {key_name} ({data_type}, {input_type}){additional_str}"
                    )
            else:
                print("  (No fields)")
        except Exception as e:
            print(f"  (Error reading fields: {e})")
            fields = []
        print()

        # 3. Reference Type - Field Mappings
        print_header("REFERENCE TYPE FIELD MAPPINGS")
        try:
            result = session.execute(
                text(
                    """
                    SELECT rt.name, f.key_name, rtf.required
                    FROM reference_type_fields rtf
                    JOIN reference_types rt ON rtf.reference_type_id = rt.id
                    JOIN fields f ON rtf.field_id = f.id
                    ORDER BY rt.name, f.key_name
                    """
                )
            )
            mappings = result.fetchall()
            if mappings:
                current_type = None
                for ref_type, field_key, required in mappings:
                    if ref_type != current_type:
                        print(f"\n  {ref_type}:")
                        current_type = ref_type
                    required_str = " [REQUIRED]" if required else ""
                    print(f"    - {field_key}{required_str}")
            else:
                print("  (No mappings)")
        except Exception as e:
            print(f"  (Error reading reference_type_fields: {e})")
            mappings = []
        print()

        # 4. Tags
        print_header("TAGS")
        try:
            result = session.execute(
                text("SELECT id, name FROM tags ORDER BY name, id")
            )
            tags = result.fetchall()
            if tags:
                for id_, name in tags:
                    print(f"  {id_}: {name}")
            else:
                print("  (No tags)")
        except Exception as e:
            print(f"  (Error reading tags: {e})")
            tags = []
        print()

        # 5. Users
        print_header("USERS")
        try:
            result = session.execute(
                text("SELECT id, username, created_at FROM users ORDER BY id")
            )
            users = result.fetchall()
            if users:
                for id_, username, created_at in users:
                    print(f"  {id_}: {username} (created: {created_at})")
            else:
                print("  (No users)")
        except Exception as e:
            session.rollback()
            print(f"  (Error reading users: {e})")
            users = []
        print()

        # 6. References (actual bibliography entries)
        print_header("REFERENCES (Bibliography Entries)")
        try:
            result = session.execute(
                text(
                    """
                    SELECT r.id, rt.name, r.bib_key, r.created_at
                    FROM single_reference r
                    JOIN reference_types rt ON r.reference_type_id = rt.id
                    ORDER BY r.created_at DESC
                    """
                )
            )
            references = result.fetchall()
            if references:
                for id_, ref_type, bib_key, created_at in references:
                    print(f"  {id_}: [{ref_type}] {bib_key} (created: {created_at})")
            else:
                print("  (No references yet)")
        except Exception as e:
            session.rollback()
            print(f"  (Error reading single_reference: {e})")
            references = []
        print()

        # 7. Reference Values (field values for references)
        print_header("REFERENCE VALUES (Field Data)")
        try:
            result = session.execute(
                text(
                    """
                    SELECT rv.id, r.bib_key, f.key_name, rv.value
                    FROM reference_values rv
                    JOIN single_reference r ON rv.reference_id = r.id
                    JOIN fields f ON rv.field_id = f.id
                    ORDER BY r.bib_key, f.key_name
                    """
                )
            )
            values = result.fetchall()
            if values:
                current_ref = None
                for id_, bib_key, field_key, value in values:
                    if bib_key != current_ref:
                        print(f"\n  {bib_key}:")
                        current_ref = bib_key
                    print(f"    {field_key}: {value}")
            else:
                print("  (No reference values yet)")
        except Exception as e:
            session.rollback()
            print(f"  (Error reading reference_values: {e})")
            values = []
        print()

        # 8. Reference Tags
        print_header("REFERENCE TAG LINKS")
        try:
            result = session.execute(
                text(
                    """
                    SELECT r.bib_key, t.name
                    FROM reference_tags rt
                    JOIN single_reference r ON rt.reference_id = r.id
                    JOIN tags t ON rt.tag_id = t.id
                    ORDER BY r.bib_key, t.name
                    """
                )
            )
            reference_tags = result.fetchall()
            if reference_tags:
                current_ref = None
                for bib_key, tag_name in reference_tags:
                    if bib_key != current_ref:
                        print(f"\n  {bib_key}:")
                        current_ref = bib_key
                    print(f"    - {tag_name}")
            else:
                print("  (No reference-tag links)")
        except Exception as e:
            session.rollback()
            print(f"  (Error reading reference_tags: {e})")
            reference_tags = []
        print()

        # 9. User -> Reference links
        print_header("USER REF LINKS")
        try:
            result = session.execute(
                text(
                    """
                    SELECT u.username, r.bib_key
                    FROM user_ref ur
                    JOIN users u ON ur.user_id = u.id
                    JOIN single_reference r ON ur.reference_id = r.id
                    ORDER BY u.username, r.bib_key
                    """
                )
            )
            user_refs = result.fetchall()
            if user_refs:
                current_user = None
                for username, bib_key in user_refs:
                    if username != current_user:
                        print(f"\n  {username}:")
                        current_user = username
                    print(f"    - {bib_key}")
            else:
                print("  (No user-ref links)")
        except Exception as e:
            session.rollback()
            print(f"  (Error reading user_ref: {e})")
            user_refs = []
        print()

        # Summary
        print_header("SUMMARY")
        print(f"  Reference Types: {len(types)}")
        print(f"  Fields: {len(fields)}")
        print(f"  Mappings: {len(mappings)}")
        print(f"  Tags: {len(tags)}")
        print(f"  Users: {len(users)}")
        print(f"  References: {len(references)}")
        print(f"  Reference Values: {len(values)}")
        print(f"  Reference Tag Links: {len(reference_tags)}")
        print(f"  User Ref Links: {len(user_refs)}")
        print()


if __name__ == "__main__":
    main()
