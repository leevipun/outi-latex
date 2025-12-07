"""Entry point for the application.

This module serves as the entry point for the Flask application.
It imports the Flask application instance and runs it on a specified host and port.
"""

import os
from src.app import app

port = int(os.getenv("PORT", 5001))

if __name__ == "__main__":
    app.run(port=port, host="0.0.0.0", debug=True)
