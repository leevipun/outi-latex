"""Flask application routes and initialization."""

from flask import jsonify, redirect, render_template, request

from config import app, test_env
from db_helper import reset_db
from utils import references
from util import get_reference_type_by_id, get_fields_for_type


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

    return (
        render_template(
            "index.html",
            reference_types=references.get_all_references(),
            error="Please select a reference type",
        ),
        400,
    )


@app.route("/add")
def add():
    """Näytä viitteen lisäyslomake

    GET /add?form=3: Muunna ID→nimi ja näytä lomake dynaamisilla kentillä
    """
    form_id = request.args.get("form")

    if not form_id:
        print("Ei form parametria!")
        return render_template("add_reference.html", selected_type=None, fields=[])

    reference_types_db = references.get_all_references()

    selected_type = None
    try:
        reference_id = int(form_id)
        selected_type = get_reference_type_by_id(reference_id, reference_types_db)
    except ValueError:
        # Jos form=article (nimi), käytä sitä suoraan
        selected_type = form_id

    # Jos tyyppiä ei löytynyt
    if not selected_type:
        return render_template("add_reference.html", selected_type=None, fields=[])

    # Hae valitun tyypin kentät form-fields.json:sta
    fields = get_fields_for_type(selected_type)

    return render_template(
        "add_reference.html", selected_type=selected_type, fields=fields
    )


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
