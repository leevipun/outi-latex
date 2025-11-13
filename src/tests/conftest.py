"""Pytest configuration for tests."""

import sys
import os

# Add the src directory to the path BEFORE any test imports
# This must run at module import time, not in fixtures
src_path = os.path.join(os.path.dirname(__file__), "..")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Import app to register all routes
    import app as app_module  # noqa: F401
    from config import app as flask_app

    # Set testing mode
    flask_app.config["TESTING"] = True

    return flask_app
