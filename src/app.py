"""Flask application routes and initialization."""

from flask import jsonify, redirect, render_template, request, flash
from src.config import app, test_env
from src.db_helper import reset_db
from src.utils import references
from src.util import get_reference_type_by_id, get_fields_for_type
from src.util import FormFieldsError, ReferenceTypeError
from src.utils.references import DatabaseError


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

    GET /add?form=article: Näytä lomake dynaamisilla kentillä
    """
    form_name = request.args.get("form")

    if not form_name:
        flash("No reference type selected", "error")
        return render_template("add_reference.html", selected_type=None, fields=[])

    # Hae valitun tyypin kentät form-fields.json:sta
    try:
        fields = get_fields_for_type(form_name)
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        fields = []

    return render_template("add_reference.html", selected_type=form_name, fields=fields)


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
