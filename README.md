# Outi LaTeX

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![codecov](https://codecov.io/gh/leevipun/outi-latex/graph/badge.svg?token=X0S5FWN837)](https://codecov.io/gh/leevipun/outi-latex) ![GitHub Actions](https://github.com/leevipun/outi-latex/actions/workflows/ci.yaml/badge.svg)

A Flask-based web application for managing reference collections with LaTeX support.

Backlog + Sprint Backlog: [https://docs.google.com/spreadsheets/d/1c9JaIyMWyLqpMv7I3L1M4DubtTQdr-XJTI_NyptITVM/edit?gid=1430592900#gid=1430592900]

CI: https://github.com/leevipun/outi-latex/actions

## 📋 Table of Contents

- [Features](#features)
- [Definition Of Done](#dod)
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

## DoD

- User storyille tulee määritellä hyväksymiskriteerit, jotka dokumentoidaan Robot Frameworkin syntaksilla
- Toteutetun koodin testikattavuuden tulee olla yli 80 %
- Testien tulee läpäistä ilman virheitä CI-palvelussa.
- Asiakas pääsee näkemään koko ajan koodin ja testien tilanteen CI-palvelusta
- Koodin ylläpidettävyyden tulee olla mahdollisimman hyvä esim (järkevä nimeäminen)
- Pylint-pisteet ≥ 8.5/10 eikä yhtään error-tason huomautusta

## 📦 Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- PostgreSQL (for the database)
- Git

## 🚀 Installation

### Option A: Using Docker (Recommended)

The easiest way to run the entire application with Docker:

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd outi-latex
```

#### 2. Run with Docker Compose

```bash
docker-compose up
```

This will:

- Start a PostgreSQL database
- Build and run the Flask application
- Automatically seed the database
- Make the app available at `http://localhost:5001`

To stop the containers:

```bash
docker-compose down
```

To remove all data:

```bash
docker-compose down -v
```

### Option B: Local Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd outi-latex
```

#### 2. Install Poetry

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

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/outi_latex
SECRET_KEY=your-secret-key-here
TEST_ENV=false
```

### Database Setup

#### Option 1: Using Docker Compose (Recommended for local development)

If you have Docker installed, the easiest way to set up PostgreSQL is:

```bash
docker-compose up -d
```

This starts a PostgreSQL container. Wait a moment for it to be ready, then proceed to seeding.

#### Option 2: Local PostgreSQL Installation

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

> Auth note: the schema now includes `users` and `user_ref` tables for login and ownership. If you already have a database, rerun the schema setup/reset before using the new auth routes. After starting the app, create your first account via `/signup`.

#### Stopping Docker Postgres

```bash
docker-compose down
```

To also remove the data volume:

```bash
docker-compose down -v
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
│   │   ├── index.html          # Main page template
│   │   ├── all.html            # All references display template
│   │   └── add_reference.html  # Add reference form template
│   ├── static/                 # Static assets
│   │   └── styles.css          # Application stylesheets
│   ├── utils/                  # Utility modules
│   │   └── references.py       # Reference management functions
│   ├── tests/                  # Unit tests (pytest)
│   │   ├── __init__.py
│   │   ├── conftest.py         # Pytest fixtures
│   │   ├── app_tests.py        # Flask application tests
│   │   ├── references_tests.py # Reference management tests
│   │   └── util_tests.py       # Utility function tests
│   └── story_tests/            # Acceptance tests (Robot Framework)
│       ├── fetch_ref_types.robot         # Reference type selection tests
│       ├── form_is_shown.robot           # Form display tests
│       ├── references_are_saved.robot    # Reference persistence tests
│       └── user_can_see_all_refs.robot   # Reference list view tests
├── pyproject.toml              # Project dependencies and configuration
├── poetry.lock                 # Locked dependency versions
├── DATABASE.md                 # Database documentation
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

The project uses a two-tier testing approach:

### Unit Tests (pytest)

Run the pytest unit test suite:

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

#### Test Coverage

Generate coverage report for Python code:

```bash
poetry run pytest --cov=src
```

This generates an HTML coverage report in `htmlcov/index.html`. Coverage reports show which lines of your Flask application are executed by tests.

**Coverage Goals:** According to the Definition of Done, test coverage must be **≥ 80%**.

### Acceptance Tests (Robot Framework)

Robot Framework tests validate user workflows end-to-end using Selenium for browser automation.

#### Running Robot Tests

Before running Robot tests, ensure:

1. `TEST_ENV=true` so the login wall is bypassed for E2E flows. Locally set it before starting Flask (`$env:TEST_ENV="true"` in PowerShell or `export TEST_ENV=true` in bash). Docker Compose already sets this for the `app` service.
1. Application is running: `poetry run python -m flask --app src.app run --debug`
2. Chrome/Chromium browser is installed
3. ChromeDriver is in PATH or available

Run all Robot tests:

```bash
poetry run robot src/story_tests/
```

Run specific test file:

```bash
poetry run robot src/story_tests/fetch_ref_types.robot
```

Run with detailed output:

```bash
poetry run robot -v DEBUG:DEBUG src/story_tests/
```

#### Test Files

- **fetch_ref_types.robot** - User can select different reference types (book, article, inproceedings)
- **form_is_shown.robot** - Correct form fields are displayed for each reference type
- **references_are_saved.robot** - References are properly saved to database
- **user_can_see_all_refs.robot** - User can view all saved references

#### Robot Test Reports

After running tests, Robot Framework generates:

- **log.html** - Detailed execution log
- **report.html** - Test summary report
- **output.xml** - Machine-readable test results

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

MIT License

Copyright (c) 2025 Leevi Ilmari Puntanen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 👥 Author

Leevi Puntanen, Otso ?, Vesa Vainio, Axel ?

---

**Last Updated:** November 2025
