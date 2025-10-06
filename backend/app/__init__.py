from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes.health import bp as health_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return {"service": "BahtBuddy API", "docs": "/api/health"}

    return app
