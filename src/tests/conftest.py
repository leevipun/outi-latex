"""Pytest configuration for tests."""

import sys
import os
import pytest

# Add the src directory to the path so tests can import modules
src_path = os.path.join(os.path.dirname(__file__), "..")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Import app module to register all routes
    import app as app_module
    from config import app
    
    # Set testing mode
    app.config["TESTING"] = True
    
    return app
