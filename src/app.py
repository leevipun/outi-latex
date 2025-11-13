"""Flask application routes and initialization."""

from flask import jsonify, redirect, render_template, request, flash

from config import app, test_env
from db_helper import reset_db
from utils import references
from utils.references import DatabaseError
from util import (
    get_reference_type_by_id,
    get_fields_for_type,
    ReferenceTypeError,
    FormFieldsError,
)


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle the main page route.

    GET: Display reference types selection form
    POST: Redirect to /add with selected reference type
    """
    if request.method == "GET":
        try:
            reference_types = references.get_all_references()
        except DatabaseError as e:
            flash(f"Database error: {str(e)}", "error")
            reference_types = []
        return render_template("index.html", reference_types=reference_types)

    reference = request.form.get("form")
    if reference:
        return redirect(f"/add?form={reference}")

    flash("Please select a reference type", "error")
    try:
        reference_types = references.get_all_references()
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        reference_types = []
    return (
        render_template(
            "index.html",
            reference_types=reference_types,
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
        flash("No reference type selected", "error")
        return render_template("add_reference.html", selected_type=None, fields=[])

    try:
        reference_types_db = references.get_all_references()
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return render_template("add_reference.html", selected_type=None, fields=[])

    selected_type = None
    try:
        reference_id = int(form_id)
        selected_type = get_reference_type_by_id(reference_id, reference_types_db)
    except ValueError:
        # Jos form=article (nimi), käytä sitä suoraan
        selected_type = form_id
    except ReferenceTypeError as e:
        flash(f"Error loading reference type: {str(e)}", "error")
        return render_template("add_reference.html", selected_type=None, fields=[])

    # Jos tyyppiä ei löytynyt
    if not selected_type:
        flash(f"Reference type not found", "error")
        return render_template("add_reference.html", selected_type=None, fields=[])

    # Hae valitun tyypin kentät form-fields.json:sta
    try:
        fields = get_fields_for_type(selected_type)
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        fields = []

    return render_template(
        "add_reference.html", selected_type=selected_type, fields=fields
    )


@app.route("/all")
def all_references():
    """See all added references listed on one page."""
    try:
        data = references.get_all_added_references()
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        data = []
        return render_template("all.html", data=data)
    
    for reference in data:
        timestamp = reference["created_at"]
        reference["created_at"] = timestamp.strftime("%H:%M, %m.%d.%y")
    return render_template("all.html", data=data)


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
