from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes.health import bp as health_bp
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance folder exists (for bahtbuddy.db)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so SQLAlchemy knows them
    from . import models

    # Enforce SQLite foreign key constraints
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        except Exception:
            pass

    # Blueprints
    app.register_blueprint(health_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return {
            "service": "BahtBuddy API",
            "database": app.config["SQLALCHEMY_DATABASE_URI"],
            "docs": "/api/health"
        }

    return app
