from flask import jsonify, render_template, request, redirect
from db_helper import reset_db
from config import app, test_env
from utils import references

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        reference_types = references.get_all_references()
        return render_template("index.html", reference_types=reference_types)
    reference = request.args.get('form')
    if reference:
        return redirect(f'/add?form={reference}')

# testausta varten oleva reitti
if test_env:
    @app.route("/reset_db")
    def reset_database():
        reset_db()
        return jsonify({ 'message': "db reset" })
