-- BibTeX-tyypit
CREATE TABLE reference_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Mahdolliset kentät
CREATE TABLE fields (
    id SERIAL PRIMARY KEY,
    key_name VARCHAR(50) NOT NULL,
    data_type VARCHAR(20) NOT NULL, -- str, int, number, date...
    input_type VARCHAR(20), -- text, number...
    additional BOOLEAN DEFAULT FALSE
);

-- Mitkä kentät kuuluu mihinkin tyyppiin + pakollisuus
CREATE TABLE reference_type_fields (
    reference_type_id INT NOT NULL REFERENCES reference_types(id),
    field_id INT NOT NULL REFERENCES fields(id),
    required BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(reference_type_id, field_id)
);

-- Yksittäinen viite
CREATE TABLE single_reference (
    id SERIAL PRIMARY KEY,
    reference_type_id INT NOT NULL REFERENCES reference_types(id),
    bib_key VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kenttäarvot
CREATE TABLE reference_values (
    id SERIAL PRIMARY KEY,
    reference_id INT NOT NULL REFERENCES single_reference(id) ON DELETE CASCADE,
    field_id INT NOT NULL REFERENCES fields(id),
    value TEXT
);

-- Avainsanat
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);