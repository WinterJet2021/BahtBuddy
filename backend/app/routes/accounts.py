from flask import Blueprint, jsonify, request
from backend.extensions.extensions import db
from backend.models.models import Account

bp = Blueprint("accounts", __name__)

@bp.get("/accounts")
def list_accounts():
    accounts = Account.query.order_by(Account.name).all()
    return jsonify([
        {
            "account_id": a.account_id,
            "name": a.name,
            "type": a.type,
            "status": a.status
        } for a in accounts
    ])

@bp.post("/accounts")
def create_account():
    data = request.get_json() or {}
    name = data.get("name")
    acc_type = data.get("type")

    if not name or not acc_type:
        return {"error": "name and type required"}, 400

    acc = Account(name=name, type=acc_type)
    db.session.add(acc)
    db.session.commit()

    return {
        "message": "Account created successfully",
        "account_id": acc.account_id,
        "name": acc.name,
        "type": acc.type
    }, 201
