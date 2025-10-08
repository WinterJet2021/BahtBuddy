from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from ...extensions import db
from ...models import Transaction, Account

bp = Blueprint("transactions", __name__)

def _date_between(query, model, start, end):
    if start:
        query = query.filter(model.date >= start)
    if end:
        query = query.filter(model.date <= end)
    return query

# Add transaction (double-entry)
@bp.post("/")
def add_txn():
    """
    Body: { "date":"YYYY-MM-DD", "amount": float,
            "debit_account_id": int, "credit_account_id": int,
            "notes": "optional" }
    """
    d = request.get_json(force=True)
    required = ("date","amount","debit_account_id","credit_account_id")
    if not all(k in d for k in required):
        return jsonify(error="date, amount, debit_account_id, credit_account_id required"), 400

    # Basic checks
    if not Account.query.get(d["debit_account_id"]) or not Account.query.get(d["credit_account_id"]):
        return jsonify(error="invalid account id(s)"), 400
    if d["debit_account_id"] == d["credit_account_id"]:
        return jsonify(error="debit and credit accounts must differ"), 400

    t = Transaction(
        date=d["date"],
        amount=float(d["amount"]),
        debit_account_id=int(d["debit_account_id"]),
        credit_account_id=int(d["credit_account_id"]),
        notes=d.get("notes")
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(txn_id=t.txn_id), 201

# Modify transaction
@bp.put("/<int:txn_id>")
def update_txn(txn_id):
    t = Transaction.query.get(txn_id)
    if not t:
        return jsonify(error="not found"), 404
    d = request.get_json(force=True)
    for k in ("date","amount","debit_account_id","credit_account_id","notes"):
        if k in d and d[k] is not None:
            setattr(t, k, d[k])
    db.session.commit()
    return jsonify(message="updated"), 200

# Delete transaction
@bp.delete("/<int:txn_id>")
def delete_txn(txn_id):
    t = Transaction.query.get(txn_id)
    if not t:
        return jsonify(error="not found"), 404
    db.session.delete(t)
    db.session.commit()
    return jsonify(message="deleted"), 200

# View transactions for a selected account with date range
@bp.get("/by-account/<int:account_id>")
def txns_by_account(account_id):
    start = request.args.get("start")  # 'YYYY-MM-DD' optional
    end   = request.args.get("end")
    q = Transaction.query.filter(
        (Transaction.debit_account_id == account_id) |
        (Transaction.credit_account_id == account_id)
    )
    q = _date_between(q, Transaction, start, end).order_by(Transaction.date.asc(), Transaction.txn_id.asc())
    items = q.all()
    return jsonify([{
        "txn_id": i.txn_id, "date": i.date, "amount": i.amount,
        "debit_account_id": i.debit_account_id, "credit_account_id": i.credit_account_id,
        "notes": i.notes
    } for i in items]), 200

# Search by source/destination (debit/credit) and date range
@bp.get("/search")
def search_txns():
    debit  = request.args.get("debit")   # int?
    credit = request.args.get("credit")  # int?
    start  = request.args.get("start")
    end    = request.args.get("end")

    q = Transaction.query
    if debit:  q = q.filter(Transaction.debit_account_id == int(debit))
    if credit: q = q.filter(Transaction.credit_account_id == int(credit))
    q = _date_between(q, Transaction, start, end).order_by(Transaction.date.asc(), Transaction.txn_id.asc())
    items = q.all()
    return jsonify([{
        "txn_id": i.txn_id, "date": i.date, "amount": i.amount,
        "debit_account_id": i.debit_account_id, "credit_account_id": i.credit_account_id,
        "notes": i.notes
    } for i in items]), 200
