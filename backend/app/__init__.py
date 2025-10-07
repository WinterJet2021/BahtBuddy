# app/__init__.py
from flask import Flask
from config.config import Config
from extensions.extensions import db, migrate
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Connect database to Flask
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/")
    def index():
        return {"message": "BahtBuddy backend is connected to SQLite ✅"}

    return app
