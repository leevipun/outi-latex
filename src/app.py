"""Flask application routes and initialization."""

from flask import jsonify, redirect, render_template, request

from config import app, test_env
from db_helper import reset_db
from utils import references
from util import get_reference_type_by_id, get_fields_for_type, load_form_fields

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

    return render_template("index.html",
        reference_types=references.get_all_references(),
        error="Please select a reference type"), 400

@app.route("/add")
def add():
    """Näytä viitteen lisäyslomake

    GET /add?form=3: Muunna ID→nimi ja näytä lomake dynaamisilla kentillä
    """
    # Hae ID URL-parametrista (esim. ?form=3)
    form_id = request.args.get('form')

    # Jos ei parametria, näytä virheviesti
    if not form_id:
        print("Ei form parametria!")
        return render_template("add_reference.html",
                             selected_type=None,
                             fields=[])

    # Hae kaikki viitetyypit tietokannasta
    reference_types_db = references.get_all_references()

    # Muunna ID→nimi (esim. 1→"article", 2→"book")
    selected_type = None
    try:
        reference_id = int(form_id)
        selected_type = get_reference_type_by_id(reference_id, reference_types_db)
        print(f"   ID {reference_id} → tyyppi: {selected_type}")
    except ValueError:
        # Jos form=article (nimi), käytä sitä suoraan
        selected_type = form_id
        print(f"Käytetään nimeä suoraan: {selected_type}")

    # Jos tyyppiä ei löytynyt
    if not selected_type:
        print(f"Tyyppiä ei löytynyt ID:llä {form_id}")
        return render_template("add_reference.html",
                             selected_type=None,
                             fields=[])

    # Hae valitun tyypin kentät form-fields.json:sta
    fields = get_fields_for_type(selected_type)
    print(f"Kenttiä löytyi: {len(fields)}")

    return render_template(
        "add_reference.html",
        selected_type=selected_type,
        fields=fields
    )
# testausta varten oleva reitti
if test_env:

    @app.route("/reset_db")
    def reset_database():
        """Reset the database (testing only)."""
        reset_db()
        return jsonify({"message": "db reset"})
