from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Account, OpeningBalance, Transaction
from app.validators import validate_account_type


bp = Blueprint("accounts", __name__)

# 1) Initialize chart of accounts from a JSON file OR defaults
@bp.post("/init")
def init_chart():
    """
    Body (optional):
      { "file_path": "backend/app/chart_of_accounts.json" }
    If not provided, use a default set.
    """
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path")

    if file_path and os.path.exists(file_path):
        accounts = json.loads(open(file_path, "r", encoding="utf-8").read())
    else:
        accounts = [
            {"name": "Cash",             "type": "asset"},
            {"name": "Bank - KBank",     "type": "asset"},
            {"name": "Credit Card",      "type": "liability"},
            {"name": "Salary",           "type": "income"},
            {"name": "Food & Dining",    "type": "expense"},
            {"name": "Transportation",   "type": "expense"},
            {"name": "Rent",             "type": "expense"},
            {"name": "Savings",          "type": "asset"},
        ]

    created = 0
    for acc in accounts:
        name = acc["name"]
        acc_type = acc["type"]
        exists = Account.query.filter_by(name=name).first()
        if not exists:
            db.session.add(Account(name=name, type=acc_type))
            created += 1
    db.session.commit()
    return jsonify(message=f"Chart initialized. Created {created} accounts."), 201

# 2) Enter opening balance
@bp.post("/opening-balance")
def add_opening_balance():
    """
    Body: { "account_id": int, "amount": float, "date": "YYYY-MM-DD" }
    """
    data = request.get_json(force=True)
    acc_id = data.get("account_id")
    amount = data.get("amount")
    date = data.get("date")
    if not (acc_id and amount is not None and date):
        return jsonify(error="account_id, amount, date required"), 400

    if not Account.query.get(acc_id):
        return jsonify(error="account_id not found"), 404

    ob = OpeningBalance(account_id=acc_id, amount=amount, date=date)
    db.session.add(ob)
    db.session.commit()
    return jsonify(message="Opening balance recorded", balance_id=ob.balance_id), 201

# 3) List accounts
@bp.get("/")
def list_accounts():
    items = Account.query.order_by(Account.account_id.asc()).all()
    return jsonify([
        {"account_id": a.account_id, "name": a.name, "type": a.type, "status": a.status}
        for a in items
    ]), 200

# 4) Current balance for a selected account
@bp.get("/<int:account_id>/balance")
def account_balance(account_id: int):
    acc = Account.query.get(account_id)
    if not acc:
        return jsonify(error="account not found"), 404

    # Opening balances
    from sqlalchemy import func
    ob_sum = db.session.query(func.coalesce(func.sum(OpeningBalance.amount), 0.0)) \
        .filter(OpeningBalance.account_id == account_id).scalar()

    # Transactions: debit - credit (simple double-entry arithmetic)
    debit_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)) \
        .filter(Transaction.debit_account_id == account_id).scalar()
    credit_sum = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)) \
        .filter(Transaction.credit_account_id == account_id).scalar()

    balance = float(ob_sum) + float(debit_sum) - float(credit_sum)
    return jsonify(account_id=account_id, name=acc.name, type=acc.type, balance=balance), 200
