from flask import Blueprint, jsonify
from sqlalchemy import text, inspect
from app.extensions import db

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    return {"status": "ok"}

@bp.get("/db")
def db_health():
    try:
        # connectivity probe
        one = db.session.execute(text("SELECT 1")).scalar()
        insp = inspect(db.engine)
        tables = insp.get_table_names()
        # optional: row counts (safe because table names come from inspect)
        counts = {}
        for t in tables:
            counts[t] = db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        return jsonify({"ok": one == 1, "tables": tables, "counts": counts})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
