import os
from flask import Flask
from extensions import db
from .routes import init_app as init_routes

def create_app():
    # Compute: <repo>/BahtBuddy/backend/instance
    backend_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # .../backend
    instance_dir  = os.path.join(backend_dir, "instance")

    # ⬇️ Pin the instance_path explicitly
    app = Flask(__name__, instance_path=instance_dir, instance_relative_config=True)

    # Ensure instance/ exists and put the SQLite file here
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "bahtbuddy.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Make sure models are imported BEFORE create_all
    from models import models as _models  # registers Account, Transaction, etc.

    with app.app_context():
        db.create_all()

    init_routes(app)

    # (Optional) quick startup log so you can see where things are
    print("[BahtBuddy] instance_path:", app.instance_path)
    print("[BahtBuddy] db:", db_path)

    return app
