from flask import Blueprint, request, jsonify
from sqlalchemy import func
from ...extensions import db
from ...models import Budget, Transaction, Account

bp = Blueprint("reports", __name__)

@bp.get("/budget-vs-actual")
def budget_vs_actual():
    """
    Query params: ?period=YYYY-MM
    Computes actual expense totals by category (via credit/debit accounts named as categories)
    and compares to budgets for that period.
    """
    period = request.args.get("period")
    if not period:
        return jsonify(error="period (YYYY-MM) is required"), 400

    # Sum actual expenses by category for the month.
    # Strategy: we assume expense categories are Accounts with type='expense'.
    # We sum amounts where that expense account appears on the DEBIT side during that period.
    # (You can adjust to your chosen convention.)
    actual_subq = db.session.query(
        Account.name.label("category"),
        func.sum(Transaction.amount).label("actual")
    ).join(Account, Account.account_id == Transaction.debit_account_id) \
     .filter(Account.type == "expense") \
     .filter(Transaction.date.like(f"{period}%")) \
     .group_by(Account.name) \
     .subquery()

    # Budgets for that period
    budgets = db.session.query(Budget.category, Budget.amount).filter(Budget.period == period).all()
    budget_map = {c: a for (c, a) in budgets}

    # Merge
    results = []
    # categories that have actuals
    rows = db.session.query(actual_subq.c.category, actual_subq.c.actual).all()
    seen = set()
    for cat, actual in rows:
        seen.add(cat)
        b = float(budget_map.get(cat, 0.0))
        results.append({"category": cat, "budget": b, "actual": float(actual), "variance": b - float(actual)})

    # categories with budgets but no actuals
    for cat, b in budget_map.items():
        if cat not in seen:
            results.append({"category": cat, "budget": float(b), "actual": 0.0, "variance": float(b)})

    # sort by largest overspend
    results.sort(key=lambda x: x["variance"])
    return jsonify(period=period, rows=results), 200
