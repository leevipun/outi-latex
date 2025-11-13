"""Entry point for the application.

This module serves as the entry point for the Flask application.
It imports the Flask application instance and runs it on a specified host and port.
"""

from src.app import app

if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0", debug=True)
