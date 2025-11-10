from flask import jsonify, render_template
from db_helper import reset_db
from config import app, test_env
from utils import references

@app.route("/")
def index():
    reference_types = references.get_all_references()
    return render_template("index.html", reference_types=reference_types)

# testausta varten oleva reitti
if test_env:
    @app.route("/reset_db")
    def reset_database():
        reset_db()
        return jsonify({ 'message': "db reset" })
