#!/usr/bin/env python3
"""
Database inspection script - view what's in your database
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

try:
    engine = create_engine(DATABASE_URL)
    print("✓ Connected to database\n")

    # Get database inspector
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables found: {', '.join(tables)}\n")

    with Session(engine) as session:
        # 1. Reference Types
        print("=" * 60)
        print("📋 REFERENCE TYPES")
        print("=" * 60)
        result = session.execute(text("SELECT id, name FROM reference_types ORDER BY id"))
        types = result.fetchall()
        if types:
            for id, name in types:
                print(f"  {id}: {name}")
        else:
            print("  (No reference types)")
        print()

        # 2. Fields
        print("=" * 60)
        print("📝 FIELDS")
        print("=" * 60)
        result = session.execute(text("""
            SELECT id, key_name, data_type, input_type, additional 
            FROM fields 
            ORDER BY id
        """))
        fields = result.fetchall()
        if fields:
            for id, key_name, data_type, input_type, additional in fields:
                additional_str = " [ADDITIONAL]" if additional else ""
                print(f"  {id}: {key_name} ({data_type}, {input_type}){additional_str}")
        else:
            print("  (No fields)")
        print()

        # 3. Reference Type - Field Mappings
        print("=" * 60)
        print("🔗 REFERENCE TYPE ↔ FIELD MAPPINGS")
        print("=" * 60)
        result = session.execute(text("""
            SELECT rt.name, f.key_name, rtf.required
            FROM reference_type_fields rtf
            JOIN reference_types rt ON rtf.reference_type_id = rt.id
            JOIN fields f ON rtf.field_id = f.id
            ORDER BY rt.name, f.key_name
        """))
        mappings = result.fetchall()
        if mappings:
            current_type = None
            for ref_type, field_key, required in mappings:
                if ref_type != current_type:
                    print(f"\n  {ref_type}:")
                    current_type = ref_type
                required_str = " [REQUIRED]" if required else ""
                print(f"    • {field_key}{required_str}")
        else:
            print("  (No mappings)")
        print()

        # 4. References (actual bibliography entries)
        print("=" * 60)
        print("📚 REFERENCES (Bibliography Entries)")
        print("=" * 60)
        try:
            result = session.execute(text("""
                SELECT r.id, rt.name, r.bib_key, r.created_at
                FROM single_reference r
                JOIN reference_types rt ON r.reference_type_id = rt.id
                ORDER BY r.created_at DESC
            """))
            references = result.fetchall()
            if references:
                for id, ref_type, bib_key, created_at in references:
                    print(f"  {id}: [{ref_type}] {bib_key} (created: {created_at})")
            else:
                print("  (No references yet)")
        except Exception as e:
            print(f"  (Table doesn't exist yet)")
            references = []
        print()

        # 5. Reference Values (field values for references)
        print("=" * 60)
        print("💾 REFERENCE VALUES (Field Data)")
        print("=" * 60)
        try:
            result = session.execute(text("""
                SELECT rv.id, r.bib_key, f.key_name, rv.value
                FROM reference_values rv
                JOIN "references" r ON rv.reference_id = r.id
                JOIN fields f ON rv.field_id = f.id
                ORDER BY r.bib_key, f.key_name
            """))
            values = result.fetchall()
            if values:
                current_ref = None
                for id, bib_key, field_key, value in values:
                    if bib_key != current_ref:
                        print(f"\n  {bib_key}:")
                        current_ref = bib_key
                    print(f"    {field_key}: {value}")
            else:
                print("  (No reference values yet)")
        except Exception as e:
            print(f"  (Table doesn't exist yet)")
            values = []
        print()

        # Summary
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"  Reference Types: {len(types)}")
        print(f"  Fields: {len(fields)}")
        print(f"  Mappings: {len(mappings)}")
        print(f"  References: {len(references)}")
        print(f"  Reference Values: {len(values)}")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    raise
