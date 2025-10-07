from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def init_extensions(app):
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
