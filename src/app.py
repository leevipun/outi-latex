"""Flask application routes and initialization."""

from flask import flash, jsonify, redirect, render_template, request

from src.config import app, test_env
from src.db_helper import reset_db
from src.util import (
    FormFieldsError,
    ReferenceTypeError,
    get_fields_for_type,
    get_reference_type_by_id,
    format_bibtex_entry,
)
from src.utils import references
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


@app.route("/save_reference", methods=["POST"])
def save_reference():
    """Tallenna uusi viite lomakkeelta tietokantaan."""
    # reference_type tulee piilokentästä <input type="hidden" name="reference_type">
    reference_type = request.form.get("reference_type")

    if not reference_type:
        flash("Viitetyyppi puuttuu.", "error")
        return redirect("/")

    # Viiteavain / cite_key (pakollinen)
    cite_key = request.form.get("cite_key", "").strip()
    if not cite_key:
        flash("Viiteavain (bib_key) on pakollinen.", "error")
        return redirect(f"/add?form={reference_type}")

    # Oletus: tietokantataulussa sarake on nimeltä 'bib_key'
    form_data = {"bib_key": cite_key}

    # Haetaan dynaamiset kentät, samoin kuin /add GET:ssä
    try:
        fields = get_fields_for_type(reference_type)
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        return redirect(f"/add?form={reference_type}")

    errors = []

    for field in fields:
        # add_reference.html käyttää field.key, joten tässäkin key
        name = field["key"]  # esim. "author", "title", "year"
        label = field.get("label", name)
        required = field.get("required", False)

        value = request.form.get(name, "").strip()

        if required and not value:
            errors.append(f"Field '{label}' is required")

        form_data[name] = value or None

    if errors:
        for msg in errors:
            flash(msg, "error")
        # back to the form, same type
        return redirect(f"/add?form={reference_type}")

    # Tallennus tietokantaan
    try:
        references.add_reference(reference_type, form_data)
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(f"/add?form={reference_type}")

    flash("Viite tallennettu!", "success")
    return redirect("/all")

@app.route("/export/bibtex")
def export_bibtex():
    """Export all references as BibTeX format"""
    try:
        data = references.get_all_added_references()

        if not data:
            return "% No references found\n", 200, {'Content-Type': 'text/plain; charset=utf-8'}
      # Muodosta BibTeX-sisältö
        bibtex_content = ""
        for ref in data:
            bibtex_entry = format_bibtex_entry(ref)
            bibtex_content += bibtex_entry + "\n\n"

        # Palauta BibTeX-tiedosto ladattavaksi
        response = app.response_class(
            bibtex_content,
            mimetype='application/x-bibtex',
            headers={
                'Content-Disposition': 'attachment; filename=references.bib',
                'Content-Type': 'application/x-bibtex; charset=utf-8'
            }
        )
        return response

# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
