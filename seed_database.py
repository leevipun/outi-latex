#!/usr/bin/env python3
"""
Database seeding script for outi-latex project using SQLAlchemy.
"""

import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

try:
    engine = create_engine(DATABASE_URL)
    print("✓ Connected to database")


    # Create tables if they don't exist
    with engine.connect() as conn:
        print("Clearing exsisting")
        """Clear all data from the database, dropping all tables except reference_types metadata."""
        print("Dropping reference_values table")
        sql = text("DROP TABLE IF EXISTS reference_values CASCADE")
        conn.execute(sql)

        print("Dropping single_reference table")
        sql = text("DROP TABLE IF EXISTS single_reference CASCADE")
        conn.execute(sql)

        print("Dropping reference_type_fields table")
        sql = text("DROP TABLE IF EXISTS reference_type_fields CASCADE")
        conn.execute(sql)

        print("Dropping fields table")
        sql = text("DROP TABLE IF EXISTS fields CASCADE")
        conn.execute(sql)

        print("Ensuring reference_types table exists before clearing contents")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reference_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """))
        sql = text("TRUNCATE TABLE reference_types RESTART IDENTITY CASCADE")
        conn.execute(sql)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reference_types (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fields (
                id SERIAL PRIMARY KEY,
                key_name VARCHAR(50) NOT NULL,
                data_type VARCHAR(20) NOT NULL,
                input_type VARCHAR(20),
                additional BOOLEAN DEFAULT FALSE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reference_type_fields (
                reference_type_id INT NOT NULL REFERENCES reference_types(id),
                field_id INT NOT NULL REFERENCES fields(id),
                required BOOLEAN DEFAULT FALSE,
                PRIMARY KEY(reference_type_id, field_id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS single_reference (
                id SERIAL PRIMARY KEY,
                reference_type_id INT NOT NULL REFERENCES reference_types(id),
                bib_key VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reference_values (
                id SERIAL PRIMARY KEY,
                reference_id INT NOT NULL REFERENCES single_reference(id) ON DELETE CASCADE,
                field_id INT NOT NULL REFERENCES fields(id),
                value TEXT
            )
        """))
        conn.commit()
    print("✓ Ensured database tables exist")

    with open('form-fields.json', 'r') as f:
        form_fields = json.load(f)
    print(f"✓ Loaded form-fields.json with {len(form_fields)} reference types")

    with Session(engine) as session:
        # Delete in child → parent order to avoid FK issues
        session.execute(text("DELETE FROM reference_type_fields"))
        session.execute(text("DELETE FROM fields"))
        session.execute(text("DELETE FROM reference_types"))
        session.commit()
        print("✓ Cleared existing data")

        # Insert reference types
        reference_types = list(form_fields.keys())
        for ref_type in reference_types:
            session.execute(
                text("""
                INSERT INTO reference_types (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
                """),
                {"name": ref_type}
            )
        session.commit()
        print(f"✓ Inserted {len(reference_types)} reference types")

        # Map reference type names → IDs
        result = session.execute(text("SELECT id, name FROM reference_types"))
        type_map = {name: id for id, name in result.fetchall()}

        # Insert fields
        unique_fields = {field['key'] for fields_list in form_fields.values() for field in fields_list}
        field_map = {}
        for key in unique_fields:
            field_data = next(
                (f for fields_list in form_fields.values() for f in fields_list if f['key'] == key),
                None
            )
            if field_data:
                result = session.execute(
                    text("""
                    INSERT INTO fields (key_name, data_type, input_type, additional)
                    VALUES (:key, :type, :input_type, :additional)
                    RETURNING id
                    """),
                    {
                        "key": key,
                        "type": field_data['type'],
                        "input_type": field_data['input-type'],
                        "additional": field_data.get('additional', False)
                    }
                )
                field_map[key] = result.scalar()

        session.commit()
        print(f"✓ Inserted {len(field_map)} unique fields")

        # Insert reference_type_fields mappings
        total_mappings = 0
        for ref_type, fields_list in form_fields.items():
            ref_type_id = type_map[ref_type]
            for field in fields_list:
                field_id = field_map[field['key']]
                session.execute(
                    text("""
                    INSERT INTO reference_type_fields (reference_type_id, field_id, required)
                    VALUES (:ref_type_id, :field_id, :required)
                    """),
                    {"ref_type_id": ref_type_id, "field_id": field_id, "required": field.get('required', False)}
                )
                total_mappings += 1

        session.commit()
        print(f"✓ Inserted {total_mappings} reference_type_field mappings")

    print("\n✅ Database seeded successfully!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    raise