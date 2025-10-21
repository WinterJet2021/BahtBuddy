# app/routes/io.py
from flask import Blueprint, request, jsonify, send_file
import csv, io
from app.extensions import db

bp = Blueprint("io", __name__)

@bp.route("/api/export/accounts", methods=["GET"])
def export_accounts():
    result = db.session.execute(db.text("SELECT * FROM accounts"))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["account_id", "name", "type", "status"])
    for row in result:
        writer.writerow(row)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name="accounts.csv")

@bp.route("/api/import/accounts", methods=["POST"])
def import_accounts():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    reader = csv.DictReader(io.StringIO(file.read().decode()))
    for row in reader:
        db.session.execute(
            db.text("INSERT INTO accounts (name, type, status) VALUES (:name, :type, :status)"),
            row
        )
    db.session.commit()
    return jsonify({"message": "Accounts imported successfully"})
