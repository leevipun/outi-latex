"""Flask application routes and initialization."""

import re
from functools import wraps

from flask import (
    Response,
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.config import app, test_env
from src.db_helper import reset_db
from src.util import (
    FormFieldsError,
    UtilError,
    format_bibtex_entry,
    get_doi_data_from_api,
    get_fields_for_type,
)
from src.utils import references
from src.utils.references import (
    DatabaseError,
    delete_reference_by_bib_key,
    filter_and_sort_search_results,
    get_reference_by_bib_key,
    get_references_filtered_sorted,
    search_reference_by_query,
    get_reference_visibility,
    get_all_added_references,
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
from src.utils.users import (
    AuthenticationError,
    UserError,
    UserExistsError,
    create_user,
    get_user_by_username,
    get_user_by_id,
    link_reference_to_user,
    verify_user_credentials,
    update_username,
    update_password,
)


def login_required(view_func):
    """Ensure the user is authenticated before accessing the route."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            next_url = request.path
            return redirect(url_for("login", next=next_url))
        return view_func(*args, **kwargs)

    return wrapper


@app.before_request
def initialize_session():
    """Initialize session group data if not already set."""
    if "group" not in session:
        session["group"] = {"userId": None, "references": []}


@app.before_request
def require_login():
    """Redirect to login for protected endpoints."""
    if test_env:
        return None

    public_endpoints = {"login", "signup", "static", "toggle_theme"}
    if test_env:
        public_endpoints.add("reset_database")

    if request.endpoint in public_endpoints or request.endpoint is None:
        return None

    if not session.get("user_id"):
        return redirect(url_for("login", next=request.path))


def login_user(user: dict):
    """Persist user info into the session."""
    session["user_id"] = user["id"]
    session["username"] = user["username"]


def logout_user():
    """Clear user info from the session."""
    session.pop("user_id", None)
    session.pop("username", None)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Simple signup route."""
    if request.method == "GET":
        return render_template("signup.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    try:
        user = create_user(username, password)
        login_user(user)
        flash("Käyttäjä luotu. Sinut kirjattiin automaattisesti sisään.", "success")
        return redirect(url_for("index"))
    except UserExistsError:
        flash("Username already exists.", "error")
    except UserError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Unexpected error creating user: {e}", "error")
    return render_template("signup.html", username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Simple login route."""
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    try:
        user = verify_user_credentials(username, password)
        login_user(user)
        flash("Kirjautuminen onnistui", "success")
        next_url = request.args.get("next") or url_for("index")
        return redirect(next_url)
    except AuthenticationError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Unexpected error logging in: {e}", "error")
    return render_template("login.html", username=username)


@app.route("/logout")
def logout():
    """Log the user out and clear session."""
    logout_user()
    session["group"] = {"userId": None, "references": []}
    flash("Uloskirjautuminen onnistui", "success")
    return redirect(url_for("login"))


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

    if not session.get("user_id"):
        flash("Kirjaudu sisään lisätäksesi viitteitä", "error")
        return redirect("/login")

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
@login_required
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
    try:
        data = references.get_all_added_references(user_id=None)
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        data = []
        return render_template("all.html", data=data, session=session)

    for reference in data:
        timestamp = reference["created_at"]
        reference["created_at"] = timestamp.strftime("%H:%M, %m.%d.%y")
    return render_template("all.html", data=data, session=session)


@app.route("/edit/<bib_key>")
@login_required
def edit_reference(bib_key):
    """Display edit form for a specific reference.

    Args:
        bib_key: Name of the reference that is to be edited.
    """
    try:
        reference = get_reference_by_bib_key(bib_key, session.get("user_id"))
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect("/all")

    if not reference:
        flash(
            f"Viitettä '{bib_key}' ei löytynyt tai sinulla ei ole oikeuksia muokata sitä",
            "error",
        )
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

    try:
        pre_filled["is_public"] = get_reference_visibility(bib_key)
    except DatabaseError as e:
        flash(f"Error loading visibility status: {str(e)}", "error")
        pre_filled["is_public"] = True

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


@app.route("/delete/<bib_key>", methods=["POST", "DELETE"])
@login_required
def delete_reference(bib_key):
    """Poista haluttu reference
    Args:
        bib_key: refen tunniste mikä halutaan poistaa
    """
    try:
        reference = get_reference_by_bib_key(bib_key, session.get("user_id"))
    except DatabaseError as e:
        if request.method == "DELETE":
            return jsonify({"success": False, "error": str(e)}), 500
        flash(f"Database error: {str(e)}", "error")
        return redirect(request.referrer or "/all")

    if not reference:
        if request.method == "DELETE":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Viitettä '{bib_key}' ei löytynyt tai sinulla ei ole oikeuksia poistaa sitä",
                    }
                ),
                403,
            )
        flash(
            f"Viitettä '{bib_key}' ei löytynyt tai sinulla ei ole oikeuksia poistaa sitä",
            "error",
        )
        return redirect("/all")

    try:
        # Poista viite KERRAN (user_id parametrilla)
        delete_reference_by_bib_key(bib_key, session.get("user_id"))

        # Poista ryhmästä jos siellä
        if bib_key in session["group"]["references"]:
            session["group"]["references"].remove(bib_key)
            session.modified = True

        # Jos DELETE-metodi (API-kutsu), palauta JSON
        if request.method == "DELETE":
            return (
                jsonify({"success": True, "message": f"Reference '{bib_key}' deleted"}),
                200,
            )

        # POST-metodi (UI), redirect
        flash(f"Viite '{bib_key}' poistettu", "success")
        return redirect(request.referrer or "/all")

    except DatabaseError as e:
        if request.method == "DELETE":
            return jsonify({"success": False, "error": str(e)}), 500
        flash(f"Database error while deleting: {str(e)}", "error")
        return redirect(request.referrer or "/all")


def _save_or_edit_reference(editing: bool):
    """Shared logic for saving and editing references.

    Args:
        editing: If True, update existing reference; if False, create new reference.
    """
    user_id = session.get("user_id")

    # Validate that the user still exists in the database
    if user_id:
        try:
            user = get_user_by_id(user_id)
            if not user:
                # User no longer exists, clear the session
                logout_user()
                flash("Your session is no longer valid. Please log in again.", "error")
                return redirect(url_for("login"))
        except UserError as e:
            flash(f"Error validating user: {str(e)}", "error")
            return redirect(url_for("login"))

    reference_type = request.form.get("reference_type")

    if not reference_type:
        flash("Viitetyyppi puuttuu.", "error")
        return redirect("/")

    # Viiteavain (pakollinen)
    cite_key = request.form.get("cite_key", "").strip()
    old_cite_key = request.form.get("old_bib_key", "").strip()
    if not cite_key:
        flash("Viiteavain (bib_key) on pakollinen.", "error")
        return redirect(f"/add?form={reference_type}")

    # Varmista että muokattava viite kuuluu käyttäjälle
    if editing:
        owned_reference = get_reference_by_bib_key(
            old_cite_key or cite_key, session.get("user_id")
        )
        if not owned_reference:
            flash(
                "Viitettä ei löytynyt tai sinulla ei ole oikeuksia muokata sitä.",
                "error",
            )
            return redirect("/all")

    form_data = {"bib_key": cite_key, "old_bib_key": old_cite_key}

    # Hae dynaamiset kentät
    try:
        fields = get_fields_for_type(reference_type)
    except FormFieldsError as e:
        flash(f"Error loading form fields: {str(e)}", "error")
        return redirect(f"/add?form={reference_type}")

    # Käsittele tagit
    new_tag_name = request.form.get("new_tag", "").strip()
    selected_tag_id = request.form.get("tag", "").strip()

    if new_tag_name:
        try:
            selected_tag_id = add_tag(new_tag_name)
            flash(f"Uusi avainsana '{new_tag_name}' lisätty", "success")
        except TagExistsError:
            try:
                selected_tag_id = get_tag_id_by_name(new_tag_name)
            except TagError as e:
                flash(f"Error fetching existing tag: {str(e)}", "error")
                return redirect(f"/add?form={reference_type}")
        except TagError as e:
            flash(f"Error adding tag: {str(e)}", "error")
            return redirect(f"/add?form={reference_type}")

    # Validoi kentät
    errors = []
    for field in fields:
        name = field["key"]
        label = field.get("label", name)
        required = field.get("required", False)
        value = request.form.get(name, "").strip()

        if required and not value:
            errors.append(f"Field '{label}' is required")

        form_data[name] = value or None

    if errors:
        for msg in errors:
            flash(msg, "error")
        return redirect(f"/add?form={reference_type}")

    # Julkisuus-asetus
    visibility = request.form.get("visibility", "public")
    form_data["is_public"] = visibility == "public"

    # Tallenna tietokantaan
    try:
        ref_id = references.add_reference(reference_type, form_data, editing=editing)
        if user_id and not editing:
            # Double-check user exists before linking
            try:
                user = get_user_by_id(user_id)
                if user:
                    link_reference_to_user(user_id, ref_id)
            except (UserError, DatabaseError) as e:
                flash(f"Warning: Could not link reference to user: {str(e)}", "warning")

        if selected_tag_id:
            try:
                add_tag_to_reference(int(selected_tag_id), ref_id)
            except (TagExistsError, TagError) as e:
                flash(f"Error associating tag to reference: {str(e)}", "error")
        else:
            delete_tag_from_reference(ref_id)

    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(f"/add?form={reference_type}")

    # Päivitä ryhmä jos tarpeen
    old_bib_key = (
        form_data.get("old_bib_key", "").strip()
        if isinstance(form_data.get("old_bib_key"), str)
        else None
    )

    if editing and old_bib_key and old_bib_key in session["group"]["references"]:
        session["group"]["references"].remove(old_bib_key)
        if form_data["bib_key"] != old_bib_key:
            session["group"]["references"].append(form_data["bib_key"])
        session.modified = True

    flash("Viite tallennettu!", "success")
    return redirect("/all")


@app.route("/save_reference", methods=["POST"])
@login_required
def save_reference():
    """Tallenna uusi viite lomakkeelta tietokantaan."""
    return _save_or_edit_reference(editing=False)


@app.route("/edit_reference", methods=["POST"])
@login_required
def edit_reference_db():
    """Tallenna muokattu viite lomakkeelta tietokantaan."""
    return _save_or_edit_reference(editing=True)


@app.route("/export/bibtex")
def export_bibtex():
    """Export all references as BibTeX format"""
    try:
        type_param = request.args.get("type", "all").strip()
        if type_param == "group" and len(session["group"]["references"]) > 0:
            data = []
            for bib_key in session["group"]["references"]:
                ref = get_reference_by_bib_key(bib_key, user_id=None)
                if ref:
                    data.append(ref)
        else:
            data = get_all_added_references(user_id=None)

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
        return redirect(request.referrer or "/all")
    except FormFieldsError as e:
        flash(f"Form fields error during BibTeX export: {str(e)}", "error")
        return redirect(request.referrer or "/all")
    except Exception as e:
        flash(f"Unexpected error during BibTeX export: {str(e)}", "error")
        return redirect(request.referrer or "/all")


@app.route("/get-doi", methods=["POST"])
@login_required
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


@app.route("/add-group/<bib_key>", methods=["POST"])
def add_group(bib_key):
    """Add a reference to a group."""
    # Hae viite ilman user_id rajoitusta -> hakee julkiset viitteet
    try:
        ref = get_reference_by_bib_key(bib_key, user_id=None)
    except DatabaseError as e:
        flash(f"Virhe: {str(e)}", "error")
        return redirect(request.referrer or "/all")

    if not ref:
        flash("Viitettä ei löytynyt", "error")
        return redirect(request.referrer or "/all")

    # Tarkista että viite on julkinen TAI käyttäjän oma
    if not ref.get("is_public"):
        # Jos yksityinen, tarkista omistajuus
        if session.get("username") != ref.get("username"):
            flash("Et voi lisätä toisen käyttäjän yksityistä viitettä ryhmään", "error")
            return redirect(request.referrer or "/all")

    if bib_key in session["group"]["references"]:
        flash("Viite on jo ryhmässä", "info")
        return redirect(request.referrer or "/all")

    session["group"]["references"].append(bib_key)
    session.modified = True
    flash("Viite lisätty ryhmään", "success")
    return redirect(request.referrer or "/all")


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
            results = search_reference_by_query(query, user_id=None)
            results = filter_and_sort_search_results(
                results,
                ref_type_filter=filter_type,
                tag_filter=tag_filter,
                sort_by=sort_by,
            )
        else:
            results = get_references_filtered_sorted(
                ref_type_filter=filter_type,
                tag_filter=tag_filter,
                sort_by=sort_by,
                user_id=None,
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


@app.route("/remove-group/<bib_key>", methods=["POST"])
def remove_group(bib_key):
    """Remove a reference from the group."""
    if bib_key not in session["group"]["references"]:
        flash("Tätä viitettä ei ole ryhmässä", "info")
        return redirect(request.referrer or "/all")
    session["group"]["references"].remove(bib_key)
    session.modified = True
    flash("Viite poistettu onnistuneesti ryhmästä", "message")
    return redirect(request.referrer or "/all")


@app.route("/group", methods=["GET"])
def view_group():
    """View references in the group."""
    try:
        data = []
        for bib_key in session["group"]["references"]:
            ref = get_reference_by_bib_key(bib_key, user_id=None)
            if ref:
                data.append(ref)
    except DatabaseError as e:
        flash(f"Database error: {str(e)}", "error")
        data = []
    return render_template("group.html", data=data, session=session)


@app.route("/user")
@login_required
def user_page():
    """Show user settings and all references for the logged-in user."""
    user_id = session.get("user_id")

    if not user_id:
        flash("Kirjaudu sisään", "error")
        return redirect("/login")

    try:
        user = get_user_by_id(user_id)

        # Hae kaikki käyttäjän viitteet (julkiset + yksityiset)
        references = get_all_added_references(user_id=user_id)

        return render_template("user.html", user=user, references=references)
    except DatabaseError as e:
        flash(f"Virhe haettaessa tietoja: {str(e)}", "error")
        return redirect("/")


@app.route("/update_username", methods=["POST"])
@login_required
def update_username_route():
    """Update user's username."""
    user_id = session.get("user_id")
    new_username = request.form.get("new_username", "").strip()
    confirm_username = request.form.get("confirm_username", "").strip()

    if not new_username or not confirm_username:
        flash("Käyttäjänimi on pakollinen", "error")
        return redirect("/user")

    if new_username != confirm_username:
        flash("Käyttäjänimet eivät täsmää", "error")
        return redirect("/user")

    try:
        update_username(user_id, new_username)
        session["username"] = new_username
        flash("Käyttäjänimi päivitetty onnistuneesti", "success")
    except UserExistsError:
        flash("Käyttäjänimi on jo käytössä", "error")
    except UserError as e:
        flash(f"Virhe: {str(e)}", "error")
    except Exception as e:
        flash(f"Odottamaton virhe: {str(e)}", "error")

    return redirect("/user")


@app.route("/update_password", methods=["POST"])
@login_required
def update_password_route():
    """Update user's password."""
    user_id = session.get("user_id")
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("Kaikki kentät ovat pakollisia", "error")
        return redirect("/user")

    if new_password != confirm_password:
        flash("Uudet salasanat eivät täsmää", "error")
        return redirect("/user")

    if len(new_password) < 8:
        flash("Salasanan tulee olla vähintään 8 merkkiä pitkä", "error")
        return redirect("/user")

    try:
        update_password(user_id, current_password, new_password)
        flash("Salasana päivitetty onnistuneesti", "success")
    except AuthenticationError:
        flash("Nykyinen salasana on väärä", "error")
    except UserError as e:
        flash(f"Virhe: {str(e)}", "error")
    except Exception as e:
        flash(f"Odottamaton virhe: {str(e)}", "error")

    return redirect("/user")


# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
