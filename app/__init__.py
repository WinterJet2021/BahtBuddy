# backend/app/__init__.py
from flask import Flask
from backend.config.config import Config
from backend.extensions.extensions import db, migrate
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # import + register blueprints INSIDE the factory to avoid NameError/circulars
    from backend.app.routes.accounts import bp as accounts_bp
    app.register_blueprint(accounts_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return {"message": "BahtBuddy backend is connected to SQLite ✅"}

    return app
