"""Flask application routes and initialization."""

from flask import flash, jsonify, redirect, render_template, request

from src.config import app, test_env
from src.db_helper import reset_db
from src.util import (
    FormFieldsError,
    UtilError,
    get_fields_for_type,
    get_doi_data_from_api,
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


@app.route("/get-doi", methods=["POST"])
def get_doi_data():
    """
    Haetaan doi:n tiedot api-rajapinnan kautta.
    """

    try:
        doi = request.form.get("doi-value")
        parsed_doi = get_doi_data_from_api(doi)
        # Hae valitun tyypin kentät form-fields.json:sta
        fields = get_fields_for_type(parsed_doi["type"])
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        fields = []
        return render_template("index.html")
    except UtilError as e:
        flash(f"Error fetching DOI data: {str(e)}", "error")
        return render_template("index.html")
    except KeyError as e:
        flash(f"Missing expected data: {str(e)}", "error")
        return render_template("index.html")
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return render_template("index.html")
    flash("DOI data fetched successfully.", "success")
    return render_template(
        "/add_reference.html",
        pre_filled_values=parsed_doi,
        fields=fields,
        selected_type=parsed_doi["type"],
    )


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
