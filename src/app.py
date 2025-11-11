from flask import redirect, render_template, request, jsonify, flash
from db_helper import reset_db
from config import app, test_env
from util import load_form_fields

@app.route("/")
def index():
    """Etusivu - näytä tyyppi-valinta"""
    form_fields = load_form_fields()
    reference_types = list(form_fields.keys())

    return render_template("index.html", reference_types=reference_types)

@app.route("/show_fields")
def show_fields():
    """Näytä valitun tyypin kentät"""
    selected_type = request.args.get('type')
    form_fields = load_form_fields()
    reference_types = list(form_fields.keys())

    fields = []
    if selected_type and selected_type in form_fields:
        fields = form_fields[selected_type]

    return render_template(
        "index.html",
        reference_types=reference_types,
        selected_type=selected_type,
        fields=fields
    )

# testausta varten oleva reitti
if test_env:
    @app.route("/reset_db")
    def reset_database():
        reset_db()
        return jsonify({ 'message': "db reset" })
