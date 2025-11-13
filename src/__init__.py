"""Flask application package initialization."""

# Import app module to register all routes when package is imported
# This must be done to ensure all Flask routes are registered before tests run
import src.app  # noqa: F401
