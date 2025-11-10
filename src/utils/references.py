from config import db
from sqlalchemy import text

def get_all_references() -> list:
    sql = text("""SELECT id, name 
             FROM reference_types 
             ORDER BY id;""")
    reference_types = db.session.execute(sql)
    return [dict(row._mapping) for row in reference_types.fetchall()]
