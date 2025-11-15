# Outi LaTeX

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Flask-based web application for managing reference collections with LaTeX support.

https://docs.google.com/spreadsheets/d/1c9JaIyMWyLqpMv7I3L1M4DubtTQdr-XJTI_NyptITVM/edit?gid=0#gid=0

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

## ✨ Features

- 📚 Manage multiple reference types
- 🎨 Clean and modern web interface with gradient design
- 🗄️ PostgreSQL database backend with SQLAlchemy ORM
- 🧪 Comprehensive test suite with pytest
- 🔧 Automatic code formatting with Black and isort
- 📊 Database seeding and management utilities

## 📦 Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- PostgreSQL (for the database)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd outi-latex
```

### 2. Install Poetry

If you don't have Poetry installed, install it from [python-poetry.org](https://python-poetry.org)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies

```bash
poetry install
```

This will install all dependencies including development tools (Black, isort, autoflake, pylint).

### 4. Activate Virtual Environment

```bash
poetry shell
```

Or prefix commands with `poetry run` to run in the virtual environment.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/outi_latex
SECRET_KEY=your-secret-key-here
TEST_ENV=false
```

### Database Setup

1. Create a PostgreSQL database:

```bash
createdb outi_latex
```

2. Run the schema:

```bash
poetry run python src/index.py
```

3. Seed the database (optional):

```bash
poetry run python seed_database.py
```

## 🏃 Running the Application

### Development Mode

```bash
poetry run python -m flask --app src.app run --debug
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
poetry run python -m flask --app src.app run
```

## 📁 Project Structure

```
outi-latex/
├── src/
│   ├── app.py                  # Flask application and routes
│   ├── config.py               # Configuration settings
│   ├── db_helper.py            # Database helper functions
│   ├── index.py                # Application entry point
│   ├── schema.sql              # Database schema
│   ├── util.py                 # Utility functions
│   ├── templates/              # HTML templates
│   │   └── index.html          # Main page template
│   │   └── all.html            # Template for all added
│   │   └── add_reference.html  # Add reference form template
│   ├── utils/                  # Utility modules
│   │   └── references.py       # Reference management functions
│   └── tests/                  # Test suite
│       └── conftest.py
│       └── e2e_tests.py
│       └── references_tests.py
│       └── util_tests.py
├── pyproject.toml              # Project dependencies and configuration
├── poetry.lock                 # Locked dependency versions
├── form-fields.json            # Form field definitions
├── seed_database.py            # Database seeding script
├── check_database.py           # Database inspection utility
└── README.md                   # This file
```

## 🛠️ Development

### Code Formatting

The project uses automatic code formatting. Format your code with:

```bash
poetry run black src/
poetry run isort src/
```

### Remove Unused Imports

```bash
poetry run autoflake --in-place --remove-all-unused-imports src/
```

### Linting

Check code quality with:

```bash
poetry run pylint src/
```

### VS Code Integration

The project includes `.vscode/settings.json` for VS Code integration:

- ✅ Auto-format on save with Black
- ✅ Auto-organize imports on save with isort
- ✅ Real-time linting with pylint

## 🧪 Testing

Run the test suite:

```bash
poetry run pytest
```

Run tests with verbose output:

```bash
poetry run pytest -v
```

Run specific test file:

```bash
poetry run pytest src/tests/references_tests.py
```

## 🗄️ Database

### Database Utilities

#### Check Database Status

```bash
poetry run python check_database.py
```

#### Reset Database (Testing Only)

```bash
curl http://localhost:5000/reset_db
```

This endpoint is only available when `TEST_ENV=true`

#### Seed Database

```bash
poetry run python seed_database.py
```

## 🌐 API Endpoints

### GET `/`

Main page - displays reference types selection form

**Response:** HTML form with dropdown of reference types

### GET `/add?form=<type_id>`

Add new reference page

**Parameters:**

- `form` (required): Reference type ID

**Response:** Add form page for the selected reference type

### GET `/reset_db` (Testing Only)

Reset the database to initial state

**Available when:** `TEST_ENV=true`

**Response:** `{ "message": "db reset" }`

## 📝 Form Fields

Form field definitions are stored in `form-fields.json`. This file defines the structure and validation rules for different reference types.

## 📚 Dependencies

### Core Dependencies

- **Flask 3.1.2** - Web framework
- **SQLAlchemy 2.0.44** - ORM
- **Flask-SQLAlchemy 3.0.0** - Flask integration for SQLAlchemy
- **psycopg2-binary 2.9.0** - PostgreSQL adapter

### Development Dependencies

- **pytest 9.0.0** - Testing framework
- **Black 24.0.0** - Code formatter
- **isort 5.13.0** - Import organizer
- **autoflake 2.0.0** - Unused import remover
- **pylint 3.0.0** - Code linter

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Format code: `poetry run black src/ && poetry run isort src/`
4. Run tests: `poetry run pytest`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature/your-feature`

## 📄 License

Add your license information here.

## 👥 Author

Add author information here.

---

**Last Updated:** November 2025
