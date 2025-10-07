# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from app.routes.health import bp as health_bp
import os, importlib
from sqlalchemy import event
from sqlalchemy.engine import Engine

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    os.makedirs(app.instance_path, exist_ok=True)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # LATE IMPORT to avoid circulars
    with app.app_context():
        importlib.import_module("app.models")  # registers models with SQLAlchemy

    # Enforce SQLite FKs
    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cur = dbapi_connection.cursor()
            cur.execute("PRAGMA foreign_keys=ON;")
            cur.close()
        except Exception:
            pass

    # blueprints
    app.register_blueprint(health_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return {
            "service": "BahtBuddy API",
            "database": app.config.get("SQLALCHEMY_DATABASE_URI"),
            "docs": "/api/health",
        }

    return app
