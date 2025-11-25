"""Flask application routes and initialization."""

from flask import flash, jsonify, redirect, render_template, request

from src.config import app, test_env
from src.db_helper import reset_db
from src.util import (
    FormFieldsError,
    UtilError,
    format_bibtex_entry,
    get_doi_data_from_api,
    get_fields_for_type,
    get_reference_type_by_id,
)
from src.utils import references
from src.utils.references import (
    DatabaseError,
    delete_reference_by_bib_key,
    get_reference_by_bib_key,
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


@app.route("/edit/<bib_key>")
def edit_reference(bib_key):
    """Display edit form for a specific reference.

    Args:
        bib_key: Name of the reference that is to be edited.
    """
    try:
        reference = get_reference_by_bib_key(bib_key)
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect("/all")

    if not reference:
        flash(f"Reference with bib_key '{bib_key}' not found", "error")
        return redirect("/all")

    try:
        fields = get_fields_for_type(reference["reference_type"])
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        return redirect("/all")

    pre_filled = {"bib_key": reference["bib_key"], **reference["fields"]}

    return render_template(
        "add_reference.html",
        selected_type=reference["reference_type"],
        fields=fields,
        pre_filled_values=pre_filled,
    )


@app.route("/delete/<bib_key>", methods=["POST"])
def delete_reference(bib_key):
    """Poista haluttu reference
    Args:
        bib_key: refen tunniste mikä halutaan poistaa
    """
    try:
        reference = get_reference_by_bib_key(bib_key)
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect("/all")
    if not reference:
        flash(f"Reference with bib_key '{bib_key}' not found", "error")
        return redirect("/all")
    try:
        delete_reference_by_bib_key(bib_key)
        flash(f"Viite '{bib_key}' poistettu", "success")
    except DatabaseError as e:
        flash(f"Database error while deleting: {str(e)}", "error")
    return redirect("/all")


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
    old_cite_key = request.form.get("old_bib_key", "").strip()
    if not cite_key:
        flash("Viiteavain (bib_key) on pakollinen.", "error")
        return redirect(f"/add?form={reference_type}")

    # Oletus: tietokantataulussa sarake on nimeltä 'bib_key'
    form_data = {"bib_key": cite_key, "old_bib_key": old_cite_key}

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
            return (
                "% No references found\n",
                200,
                {"Content-Type": "text/plain; charset=utf-8"},
            )
        # Muodosta BibTeX-sisältö
        bibtex_content = ""
        for ref in data:
            bibtex_entry = format_bibtex_entry(ref)
            bibtex_content += bibtex_entry + "\n\n"

        # Palauta BibTeX-tiedosto ladattavaksi
        response = app.response_class(
            bibtex_content,
            mimetype="application/x-bibtex",
            headers={
                "Content-Disposition": "attachment; filename=references.bib",
                "Content-Type": "application/x-bibtex; charset=utf-8",
            },
        )
        return response

    except DatabaseError as e:
        flash(f"Database error during BibTeX export: {str(e)}", "error")
        return redirect("/all")
    except FormFieldsError as e:
        flash(f"Form fields error during BibTeX export: {str(e)}", "error")
        return redirect("/all")
    except Exception as e:
        flash(f"Unexpected error during BibTeX export: {str(e)}", "error")
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


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html", data=[])

    query = request.form.get("search-query")
    result = references.search_reference_by_query(query)
    return render_template("search.html", data=result)


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
