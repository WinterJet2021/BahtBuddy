from flask import Blueprint, request, jsonify
from ...extensions import db
from ...models import Budget

bp = Blueprint("budgets", __name__)

@bp.post("/")
def create_budget():
    """
    Body: { "category":"Food & Dining", "amount": 5000, "period":"2025-10" }
    """
    d = request.get_json(force=True)
    if not all(k in d for k in ("category","amount","period")):
        return jsonify(error="category, amount, period required"), 400
    b = Budget(category=d["category"], amount=float(d["amount"]), period=d["period"])
    db.session.add(b)
    db.session.commit()
    return jsonify(budget_id=b.budget_id), 201

@bp.put("/<int:budget_id>")
def update_budget(budget_id):
    b = Budget.query.get(budget_id)
    if not b:
        return jsonify(error="not found"), 404
    d = request.get_json(force=True)
    for k in ("category","amount","period"):
        if k in d and d[k] is not None:
            setattr(b, k, d[k] if k!="amount" else float(d[k]))
    db.session.commit()
    return jsonify(message="updated"), 200

@bp.get("/")
def list_budgets():
    items = Budget.query.order_by(Budget.period.desc(), Budget.category.asc()).all()
    return jsonify([{
        "budget_id": i.budget_id, "category": i.category,
        "amount": i.amount, "period": i.period
    } for i in items]), 200
