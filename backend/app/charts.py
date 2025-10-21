# app/routes/charts.py
from flask import Blueprint, jsonify
from app.extensions import db

bp = Blueprint("charts", __name__)

@bp.route("/api/charts/income_expense")
def income_expense_chart():
    query = """
        SELECT a.type, SUM(t.amount) AS total
        FROM transactions t
        JOIN accounts a ON t.debit_account_id = a.account_id
        GROUP BY a.type
    """
    data = [dict(row) for row in db.session.execute(db.text(query))]
    return jsonify({"chart_data": data})
