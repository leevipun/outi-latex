"""Flask application routes and initialization."""

import re

from flask import (
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    session
)

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
    get_references_filtered_sorted,
    search_reference_by_query,
    filter_and_sort_search_results,
)
from src.utils.tags import (
    TagError,
    TagExistsError,
    add_tag,
    add_tag_to_reference,
    delete_tag_from_reference,
    get_tag_by_reference,
    get_tag_id_by_name,
    get_tags,
)

@app.before_request
def initialize_session():
    """Initialize session group data if not already set."""
    if "group" not in session:
        session["group"] = {
            "userId": None,
            "references": []
        }

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

    # Hae tagit
    try:
        tags = get_tags()
    except TagError as e:
        flash(f"Error loading tags: {str(e)}", "error")
        tags = []

    return render_template(
        "add_reference.html", selected_type=form_name, fields=fields, tags=tags
    )


@app.route("/all")
def all_references():
    """See all added references listed on one page."""
    print(session)
    try:
        data = references.get_all_added_references()
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        data = []
        return render_template("all.html", data=data, session=session["group"])

    for reference in data:
        timestamp = reference["created_at"]
        reference["created_at"] = timestamp.strftime("%H:%M, %m.%d.%y")
    return render_template("all.html", data=data, session=session)


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

    try:
        tag = get_tag_by_reference(reference["id"])
    except TagError as e:
        flash(f"Error loading tag for reference: {str(e)}", "error")

    pre_filled = {"bib_key": reference["bib_key"], **reference["fields"]}
    if tag:
        pre_filled["tag"] = tag

    # Hae tagit
    try:
        tags = get_tags()
    except TagError as e:
        flash(f"Error loading tags: {str(e)}", "error")
        tags = []

    return render_template(
        "add_reference.html",
        selected_type=reference["reference_type"],
        fields=fields,
        pre_filled_values=pre_filled,
        tags=tags,
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

    new_tag_name = request.form.get("new_tag", "").strip()
    selected_tag_id = request.form.get("tag", "").strip()

    if new_tag_name:
        try:
            selected_tag_id = add_tag(new_tag_name)
            flash(f"Uusi avainsana '{new_tag_name}' lisätty", "success")
        except TagExistsError:
            # Avainsana on jo olemassa, haetaan sen ID
            try:
                selected_tag_id = get_tag_id_by_name(new_tag_name)
            except TagError as e:
                flash(f"Error fetching existing tag: {str(e)}", "error")
                return redirect(f"/add?form={reference_type}")
        except TagError as e:
            flash(f"Error adding tag: {str(e)}", "error")
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
        ref_id = references.add_reference(reference_type, form_data)
        if selected_tag_id:
            try:
                add_tag_to_reference(int(selected_tag_id), ref_id)
            except (TagExistsError, TagError) as e:
                flash(f"Error associating tag to reference: {str(e)}", "error")
        else:
            # Poista mahdollinen vanha avainsana
            delete_tag_from_reference(ref_id)

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
        if not doi:
            flash("DOI value is required.", "error")
            return render_template("index.html")
        if not re.match(r"^10\.\d{4,}/\S+$", doi):
            flash("Invalid DOI format.", "error")
            return render_template("index.html")

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
    try:
        tags = get_tags()
    except TagError as e:
        flash(f"Error loading tags: {str(e)}", "error")
        tags = []

    try:
        reference_types = references.get_all_references()
    except DatabaseError as e:
        flash(f"Error loading reference types: {str(e)}", "error")
        reference_types = []

    if request.method == "GET":
        return render_template(
            "search.html", tags=tags, reference_types=reference_types
        )

    query = request.form.get("search-query", "").strip()
    filter_type = request.form.get("filter-type", "").strip()
    tag_filter = request.form.get("tag-filter", "").strip()
    sort_by = request.form.get("sort-by", "newest")

    try:
        if query:
            results = search_reference_by_query(query)
            results = filter_and_sort_search_results(
                results,
                ref_type_filter=filter_type,
                tag_filter=tag_filter,
                sort_by=sort_by,
            )
        else:
            results = get_references_filtered_sorted(
                ref_type_filter=filter_type, tag_filter=tag_filter, sort_by=sort_by
            )

        return render_template(
            "search.html",
            data=results,
            query=query,
            filter_type=filter_type,
            tag_filter=tag_filter,
            sort_by=sort_by,
            tags=tags,
            reference_types=reference_types,
        )
    except DatabaseError as e:
        flash(f"Virhe haettaessa viitteitä: {e}", "error")
        return render_template(
            "search.html", tags=tags, reference_types=reference_types
        )


@app.context_processor
def inject_theme():
    """Käytetty teema saataville kaikkiin reitteihin (light/dark) ja sitä kautta kaikkiin temploihin."""
    theme = request.cookies.get("theme", "light")  # defaultti
    return {"theme": theme}


@app.route("/toggle-theme")
def toggle_theme():
    """Voi vaihdella teemaa (redirectaa takaisin)."""
    current = request.cookies.get("theme", "light")
    new = "dark" if current == "light" else "light"

    # Redirect tai etusivu error tilanteessa
    next_url = request.referrer or url_for("index")

    resp = make_response(redirect(next_url))
    # 1 vuoden cookie:D
    resp.set_cookie("theme", new, max_age=60 * 60 * 24 * 365)
    return resp


@app.route("/add-group/<bib_key>", methods=["POST"])
def add_group(bib_key):
    """Add a reference to a group."""
    if bib_key in session["group"]["references"]:
        flash("Tämä viite on jo lisätty ryhmään", "info")
        return redirect("/all")
    session["group"]["references"].append(bib_key)
    session.modified = True
    flash("Viite lisätty onnistuneesti ryhmään", "message")
    return redirect("/all")

# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
