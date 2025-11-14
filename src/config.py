"""Flask application configuration and database setup."""
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

test_env = getenv("TEST_ENV") == "true"
print(f"Test environment: {test_env}")

# Get the directory where this config file is located
BASE_DIR = Path(__file__).parent

app = Flask(__name__, static_folder=str(BASE_DIR / "static"), static_url_path="/static")
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
