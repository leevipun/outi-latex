# Database Documentation - outi-latex

## Overview

The outi-latex project uses a PostgreSQL database to manage BibTeX bibliography references. The database is designed to store different types of academic references (articles, books, conference papers, theses, etc.) with flexible field definitions.

## Database Architecture

### Core Concept

The database follows a relational model with three main layers:

1. **Reference Types** - BibTeX entry types (article, book, inproceedings, etc.)
2. **Fields** - Possible metadata fields (author, title, year, etc.)
3. **References** - Actual bibliography entries with their field values

This design allows:

- Different reference types to have different required/optional fields
- Flexible field definitions shared across types
- Clean separation between schema and data

---

## Database Schema

### Table: `reference_types`

Stores the available BibTeX entry types.

```sql
CREATE TABLE reference_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);
```

**Columns:**

- `id` - Unique identifier (primary key)
- `name` - BibTeX type name (e.g., "article", "book", "inproceedings")

**Supported Types:**

- `article` - Journal articles
- `book` - Books
- `inproceedings` - Conference papers
- `inbook` - Chapters in books
- `incollection` - Articles in edited collections
- `misc` - Miscellaneous entries
- `phdthesis` - PhD dissertations
- `mastersthesis` - Master's theses
- `techreport` - Technical reports
- `unpublished` - Unpublished works

---

### Table: `fields`

Stores all available metadata fields that can be associated with references.

```sql
CREATE TABLE fields (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(50) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    input_type VARCHAR(20),
    additional BOOLEAN DEFAULT FALSE
);
```

**Columns:**

- `id` - Unique identifier (primary key)
- `key_name` - Field identifier (e.g., "author", "title", "year")
- `data_type` - Data type stored (e.g., "str", "int", "number", "date")
- `input_type` - HTML input type for forms (e.g., "text", "number")
- `additional` - Boolean flag indicating if this is an optional/additional field

**Common Fields:**

- Required across multiple types: `author`, `title`, `year`
- Optional: `volume`, `number`, `pages`, `doi`, `isbn`, `url`
- Type-specific: `journal`, `booktitle`, `publisher`, `school`

---

### Table: `reference_type_fields`

Junction table mapping reference types to fields with requirement flags.

```sql
CREATE TABLE reference_type_fields (
    reference_type_id INT NOT NULL REFERENCES reference_types(id),
    field_id INT NOT NULL REFERENCES fields(id),
    required BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(reference_type_id, field_id)
);
```

**Columns:**

- `reference_type_id` - Foreign key to `reference_types`
- `field_id` - Foreign key to `fields`
- `required` - Whether this field is required for this reference type

**Purpose:**
Defines the schema for each reference type. For example:

- Article requires: author, title, journal, year
- Article optionally includes: volume, number, pages, doi, publisher

---

### Table: `references`

Stores individual bibliography entries.

```sql
CREATE TABLE single_reference (
    id SERIAL PRIMARY KEY,
    reference_type_id INT NOT NULL REFERENCES reference_types(id),
    bib_key VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**

- `id` - Unique identifier (primary key)
- `reference_type_id` - Foreign key to `reference_types` (type of this reference)
- `bib_key` - Unique citation key used in LaTeX documents (e.g., "Smith2023", "Johnson_etal2022")
- `created_at` - Timestamp when the reference was created

---

### Table: `reference_values`

Stores field values for each reference (actual metadata).

```sql
CREATE TABLE reference_values (
    id SERIAL PRIMARY KEY,
    reference_id INT NOT NULL REFERENCES single_reference(id) ON DELETE CASCADE,
    field_id INT NOT NULL REFERENCES fields(id),
    value TEXT
);
```

**Columns:**

- `id` - Unique identifier (primary key)
- `reference_id` - Foreign key to `references`
- `field_id` - Foreign key to `fields`
- `value` - The actual value (stored as TEXT, can represent str, int, dates, etc.)

**Purpose:**
Stores the actual metadata for references. For example:

- Reference "Smith2023" + Field "author" = "John Smith, Jane Doe"
- Reference "Smith2023" + Field "year" = "2023"

---

### Table: `tags`

Stores reference categories.

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);
```

**Columns:**

- `id` - Unique identifier (primary key)
- `name` - Tag name (e.g., "machine-learning", "computer-vision", "nlp")

**Purpose:**
Allows categorization and organization of references using keywords/tags.

---

### Table: `reference_tags`

Junction table implementing many-to-many relationship between references and tags.

```sql
CREATE TABLE reference_tags (
    reference_id INT NOT NULL REFERENCES single_reference(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY(reference_id, tag_id)
);
```

**Columns:**

- `reference_id` - Foreign key to `single_reference`
- `tag_id` - Foreign key to `tags`

**Purpose:**
Enables multiple tags per reference and multiple references per tag. For example:

- Reference "Smith2023" can have tags: "machine-learning", "nlp", "transformers"
- Tag "machine-learning" can be associated with many references

---

## Data Relationships

```
reference_types (1) ──┬──→ (Many) reference_type_fields
                      │
                      └──→ (Many) single_reference

fields (1) ──┬──→ (Many) reference_type_fields
             │
             └──→ (Many) reference_values

single_reference (1) ──┬──→ (Many) reference_values
                       │
                       └──→ (Many) reference_tags

tags (1) ──→ (Many) reference_tags
```

---

## Setup & Seeding

### Database Initialization

#### Using `db_helper.py`

```python
from db_helper import setup_db
from config import app

with app.app_context():
    setup_db()
```

This function:

1. Checks for existing tables
2. Drops all tables if they exist
3. Creates new tables from `schema.sql`

#### Using `seed_database.py`

```bash
python seed_database.py
```

This script:

1. Reads field definitions from `form-fields.json`
2. Creates/ensures all schema tables exist
3. Clears existing data
4. Inserts all reference types from the JSON
5. Inserts all unique fields from the JSON
6. Creates mappings between types and fields

**Requirements:**

- `DATABASE_URL` environment variable set
- `form-fields.json` file present in project root

---

## Common Queries

### 1. View All Reference Types

```sql
SELECT id, name
FROM reference_types
ORDER BY id;
```

**Returns:** All available BibTeX entry types in the database.

**Example Output:**

```
 id |     name
----+---------------
  1 | article
  2 | book
  3 | inproceedings
```

---

### 2. View All Fields

```sql
SELECT id, key_name, data_type, input_type, additional
FROM fields
ORDER BY id;
```

**Returns:** All available metadata fields with their types.

**Example Output:**

```
 id | key_name | data_type | input_type | additional
----+----------+-----------+------------+------------
  1 | author   | str       | text       | f
  2 | title    | str       | text       | f
  3 | year     | int       | number     | f
```

---

### 3. View Field Requirements for a Reference Type

```sql
SELECT f.key_name, rtf.required
FROM reference_type_fields rtf
JOIN fields f ON rtf.field_id = f.id
JOIN reference_types rt ON rtf.reference_type_id = rt.id
WHERE rt.name = 'article'
ORDER BY f.key_name;
```

**Returns:** All fields for a specific reference type with required flags.

**Example Output:**

```
 key_name | required
----------+----------
 author   | t
 title    | t
 journal  | t
 year     | t
 volume   | f
 doi      | f
```

---

### 4. View All Type ↔ Field Mappings

```sql
SELECT rt.name, f.key_name, rtf.required
FROM reference_type_fields rtf
JOIN reference_types rt ON rtf.reference_type_id = rt.id
JOIN fields f ON rtf.field_id = f.id
ORDER BY rt.name, f.key_name;
```

**Returns:** Complete mapping matrix of types to fields.

**Use Case:** Understanding the schema structure, validating forms.

---

### 5. Get a Specific Reference

```sql
SELECT r.id, rt.name, r.bib_key, r.created_at
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
WHERE r.bib_key = 'Smith2023'
LIMIT 1;
```

**Returns:** Single reference with its type and metadata.

---

### 6. Get All References of a Type

```sql
SELECT r.id, r.bib_key, r.created_at
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
WHERE rt.name = 'article'
ORDER BY r.created_at DESC;
```

**Returns:** All bibliography entries of a specific type.

---

### 7. View a Reference's Field Values

```sql
SELECT f.key_name, rv.value
FROM reference_values rv
JOIN fields f ON rv.field_id = f.id
WHERE rv.reference_id = 1
ORDER BY f.key_name;
```

**Returns:** All metadata for a specific reference.

**Example Output:**

```
  key_name   |                value
--------------+--------------------------------------
 author       | John Smith and Jane Doe
 journal      | Nature Machine Intelligence
 pages        | 42-58
 title        | Deep Learning in Practice
 volume       | 2
 year         | 2023
```

---

### 8. View All References with Full Details

```sql
SELECT r.id, r.bib_key, rt.name, f.key_name, rv.value
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
LEFT JOIN reference_values rv ON rv.reference_id = r.id
LEFT JOIN fields f ON rv.field_id = f.id
ORDER BY r.bib_key, f.key_name;
```

**Returns:** Complete data dump - all references with all their field values.

**Use Case:** Data export, backups, comprehensive audits.

---

### 9. Find References Missing Required Fields

```sql
SELECT DISTINCT r.id, r.bib_key, rt.name, f.key_name
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
JOIN reference_type_fields rtf ON rt.id = rtf.reference_type_id
JOIN fields f ON rtf.field_id = f.id
WHERE rtf.required = TRUE
  AND NOT EXISTS (
    SELECT 1 FROM reference_values rv
    WHERE rv.reference_id = r.id
    AND rv.field_id = f.id
    AND rv.value IS NOT NULL
  )
ORDER BY r.bib_key, f.key_name;
```

**Returns:** References that violate the required field constraint.

**Use Case:** Data validation, identifying incomplete entries.

---

### 10. Count References by Type

```sql
SELECT rt.name, COUNT(r.id) as count
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
GROUP BY rt.name
ORDER BY count DESC;
```

**Returns:** Statistics on reference distribution.

**Example Output:**

```
      name      | count
-----------------+-------
 article         |    42
 inproceedings   |    28
 book            |    12
 misc            |     5
```

---

### 11. Search References by Field Value

```sql
SELECT r.id, r.bib_key, rt.name, f.key_name, rv.value
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
JOIN reference_values rv ON r.id = rv.reference_id
JOIN fields f ON rv.field_id = f.id
WHERE f.key_name = 'author'
  AND rv.value ILIKE '%Smith%'
ORDER BY r.bib_key;
```

**Returns:** References matching a search term in a specific field.

**Use Case:** Finding references by author, keyword, etc.

---

### 12. Export References to BibTeX Format

```sql
SELECT r.bib_key, rt.name,
       json_object_agg(f.key_name, rv.value) as fields
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
LEFT JOIN reference_values rv ON r.id = rv.reference_id
LEFT JOIN fields f ON rv.field_id = f.id
GROUP BY r.id, r.bib_key, rt.name
ORDER BY r.bib_key;
```

**Returns:** Structured data suitable for BibTeX generation.

---

### 13. View All Tags

```sql
SELECT id, name
FROM tags
ORDER BY name;
```

**Returns:** All available tags in alphabetical order.

**Use Case:** Displaying available tags for selection, tag management.

---

### 14. View Tags for a Specific Reference

```sql
SELECT t.id, t.name
FROM tags t
JOIN reference_tags rt ON t.id = rt.tag_id
JOIN single_reference r ON rt.reference_id = r.id
WHERE r.bib_key = 'Smith2023'
ORDER BY t.name;
```

**Returns:** All tags associated with a specific reference.

**Example Output:**

```
 id |      name
----+------------------
  3 | machine-learning
  5 | nlp
  7 | transformers
```

---

### 15. Find References by Tag

```sql
SELECT r.id, r.bib_key, rt.name as reference_type
FROM single_reference r
JOIN reference_types rt ON r.reference_type_id = rt.id
JOIN reference_tags reftag ON r.id = reftag.reference_id
JOIN tags t ON reftag.tag_id = t.id
WHERE t.name = 'machine-learning'
ORDER BY r.bib_key;
```

**Returns:** All references tagged with a specific tag.

**Use Case:** Filtering references by topic/category.

---

### 16. Count References per Tag

```sql
SELECT t.name, COUNT(rt.reference_id) as reference_count
FROM tags t
LEFT JOIN reference_tags rt ON t.id = rt.tag_id
GROUP BY t.id, t.name
ORDER BY reference_count DESC, t.name;
```

**Returns:** Tag usage statistics.

**Example Output:**

```
       name        | reference_count
-------------------+-----------------
 machine-learning  |              15
 computer-vision   |              12
 nlp               |               8
 reinforcement     |               3
 unused-tag        |               0
```

---

### 17. Find References with Multiple Specific Tags

```sql
SELECT r.id, r.bib_key
FROM single_reference r
WHERE EXISTS (
    SELECT 1 FROM reference_tags rt
    JOIN tags t ON rt.tag_id = t.id
    WHERE rt.reference_id = r.id AND t.name = 'machine-learning'
)
AND EXISTS (
    SELECT 1 FROM reference_tags rt
    JOIN tags t ON rt.tag_id = t.id
    WHERE rt.reference_id = r.id AND t.name = 'nlp'
)
ORDER BY r.bib_key;
```

**Returns:** References that have both specified tags (AND logic).

**Use Case:** Advanced filtering, finding references in intersection of topics.

---

## Python Scripts

### `check_database.py`

Inspection utility to view the current state of the database.

**Usage:**

```bash
python check_database.py
```

**Output Sections:**

1. **REFERENCE TYPES** - All BibTeX entry types defined
2. **FIELDS** - All metadata fields available
3. **REFERENCE TYPE ↔ FIELD MAPPINGS** - Schema structure
4. **REFERENCES** - All bibliography entries with creation dates
5. **REFERENCE VALUES** - Field values organized by reference
6. **SUMMARY** - Count statistics

**Key Queries Used:**

- `SELECT id, name FROM reference_types ORDER BY id`
- `SELECT * FROM fields ORDER BY id`
- Multi-join query showing type-field mappings with required flags
- `SELECT r.id, rt.name, r.bib_key, r.created_at FROM single_reference r...`
- Nested joins to display all field values per reference

---

### `seed_database.py`

Population script to initialize database with schema from `form-fields.json`.

**Usage:**

```bash
python seed_database.py
```

**Process:**

1. Connects to database via `DATABASE_URL`
2. Drops existing tables (in FK-safe order):
   - `reference_values`
   - `single_reference`
   - `reference_tags`
   - `tags`
   - `reference_type_fields`
   - `fields`
   - Clears `reference_types` table
3. Creates all tables if missing:
   - `reference_types`
   - `fields`
   - `reference_type_fields`
   - `tags`
   - `single_reference`
   - `reference_tags`
   - `reference_values`
4. Reads `form-fields.json` structure
5. Inserts all reference types
6. Inserts all unique fields with metadata
7. Creates type-field mappings with required flags

**Key Operations:**

```python
# Insert with conflict handling
INSERT INTO reference_types (name)
VALUES (:name)
ON CONFLICT (name) DO NOTHING

# Bulk insert fields
INSERT INTO fields (key_name, data_type, input_type, additional)
VALUES (:key, :type, :input_type, :additional)

# Create mappings
INSERT INTO reference_type_fields (reference_type_id, field_id, required)
VALUES (:ref_type_id, :field_id, :required)
```

**Output:**
```
✓ Connected to database
Clearing exsisting
Dropping reference_values table
Dropping single_reference table
Dropping tags table
Dropping reference_type_fields table
Dropping fields table
Ensuring reference_types table exists before clearing contents
✓ Ensured database tables exist
✓ Loaded form-fields.json with N reference types
✓ Cleared existing data
✓ Inserted N reference types
✓ Inserted N unique fields
✓ Inserted N reference_type_field mappings

✅ Database seeded successfully!
```

---

## Connection & Configuration

### Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/outi_latex
```

### Python Connection

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(os.getenv("DATABASE_URL"))

with Session(engine) as session:
    result = session.execute(text("SELECT ..."))
    data = result.fetchall()
```

---

## Best Practices

### Querying

1. **Always use parameterized queries** to prevent SQL injection:

   ```python
   session.execute(
       text("SELECT * FROM fields WHERE key_name = :name"),
       {"name": user_input}
   )
   ```

2. **Use joins carefully** - The reference system requires multiple joins:

   ```python
   # Good: explicit joins with clear relationships
   result = session.execute(text("""
       SELECT r.bib_key, f.key_name, rv.value
       FROM single_reference r
       JOIN reference_values rv ON r.id = rv.reference_id
       JOIN fields f ON rv.field_id = f.id
   """))
   ```

3. **Handle missing data** - Use LEFT JOIN when values might be NULL

### Data Integrity

1. **Foreign Key Constraints** - All tables enforce referential integrity
2. **Cascade Delete** - Deleting a reference cascades to `reference_values`
3. **Unique Constraints** - `bib_key` must be unique across references
4. **Required Fields Validation** - Check `reference_type_fields.required` before allowing NULL

### Performance

1. **Indexes** - Primary keys are indexed by default
2. **Consider adding indexes** for frequently queried columns:
   ```sql
   CREATE INDEX idx_references_type ON references(reference_type_id);
   CREATE INDEX idx_values_reference ON reference_values(reference_id);
   CREATE INDEX idx_bib_key ON references(bib_key);
   ```

---

## Common Operations

### Adding a New Reference

```python
with Session(engine) as session:
    # 1. Get reference type
    ref_type = session.execute(
        text("SELECT id FROM reference_types WHERE name = :name"),
        {"name": "article"}
    ).scalar()

    # 2. Create reference
    session.execute(
        text("""
            INSERT INTO single_reference (reference_type_id, bib_key)
            VALUES (:type_id, :key)
        """),
        {"type_id": ref_type, "key": "Smith2023"}
    )

    # 3. Get reference ID
    ref_id = session.execute(
        text("SELECT id FROM single_reference WHERE bib_key = :key"),
        {"key": "Smith2023"}
    ).scalar()

    # 4. Insert field values
    session.execute(
        text("""
            INSERT INTO reference_values (reference_id, field_id, value)
            SELECT :ref_id, id, :value FROM fields WHERE key_name = :field_name
        """),
        {"ref_id": ref_id, "field_name": "author", "value": "John Smith"}
    )

    session.commit()
```

### Updating a Field Value

```python
session.execute(
    text("""
        UPDATE reference_values
        SET value = :new_value
        WHERE reference_id = :ref_id
          AND field_id = (SELECT id FROM fields WHERE key_name = :field_name)
    """),
    {"ref_id": 1, "field_name": "year", "new_value": "2024"}
)
session.commit()
```

### Deleting a Reference

```python
session.execute(
    text("DELETE FROM single_reference WHERE id = :id"),
    {"id": 1}
)
session.commit()
```

(Automatically cascades to `reference_values` and `reference_tags`)

---

### Adding Tags to a Reference

```python
with Session(engine) as session:
    # 1. Create tag if it doesn't exist
    session.execute(
        text("""
            INSERT INTO tags (name)
            VALUES (:tag_name)
            ON CONFLICT (name) DO NOTHING
        """),
        {"tag_name": "machine-learning"}
    )
    
    # 2. Get tag ID
    tag_id = session.execute(
        text("SELECT id FROM tags WHERE name = :name"),
        {"name": "machine-learning"}
    ).scalar()
    
    # 3. Associate tag with reference
    session.execute(
        text("""
            INSERT INTO reference_tags (reference_id, tag_id)
            VALUES (:ref_id, :tag_id)
            ON CONFLICT DO NOTHING
        """),
        {"ref_id": 1, "tag_id": tag_id}
    )
    
    session.commit()
```

### Removing a Tag from a Reference

```python
session.execute(
    text("""
        DELETE FROM reference_tags
        WHERE reference_id = :ref_id
          AND tag_id = (SELECT id FROM tags WHERE name = :tag_name)
    """),
    {"ref_id": 1, "tag_name": "machine-learning"}
)
session.commit()
```

### Getting All Tags for a Reference

```python
result = session.execute(
    text("""
        SELECT t.name
        FROM tags t
        JOIN reference_tags rt ON t.id = rt.tag_id
        WHERE rt.reference_id = :ref_id
        ORDER BY t.name
    """),
    {"ref_id": 1}
)
tags = [row[0] for row in result.fetchall()]
```

---

## Troubleshooting

### ERROR: Relation Does Not Exist

**Cause:** Tables haven't been created yet
**Solution:** Run `python seed_database.py` or call `setup_db()`

### ERROR: Foreign Key Violation

**Cause:** Trying to insert/update with non-existent reference IDs
**Solution:** Verify the foreign key ID exists first

### Missing Required Fields

**Cause:** Inserted reference without populating required fields
**Solution:** Check `reference_type_fields WHERE required = TRUE` and populate all

### Duplicate bib_key

**Cause:** Trying to insert a reference with an existing citation key
**Solution:** Use unique keys or update instead of insert

---

## Summary

The database design provides:

- **Flexibility** - Different reference types have different field requirements
- **Integrity** - Foreign keys and constraints prevent invalid data
- **Scalability** - Easy to add new reference types, fields, and tags
- **Maintainability** - Clear separation of concerns (types, fields, values, tags)
- **Organization** - Tag system enables categorization and filtering of references

Key tables to remember:

- `reference_types` - What types exist (article, book, etc.)
- `fields` - What fields are available (author, title, etc.)
- `reference_type_fields` - Which fields apply to which types
- `single_reference` - The actual bibliography entries
- `reference_values` - The field values for each entry
- `tags` - Available keyword tags for categorization
- `reference_tags` - Many-to-many relationship between references and tags
