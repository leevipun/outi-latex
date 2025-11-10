"""Flask application routes and initialization."""
from flask import jsonify, redirect, render_template, request

from config import app, test_env
from db_helper import reset_db
from utils import references


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle the main page route.

    GET: Display reference types selection form
    POST: Redirect to /add with selected reference type
    """
    if request.method == "GET":
        reference_types = references.get_all_references()
        return render_template("index.html", reference_types=reference_types)
    reference = request.form.get("form")
    if reference:
        return redirect(f"/add?form={reference}")
    return None


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
