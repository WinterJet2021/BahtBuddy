"""
app/extensions.py
-----------------
Central place to define and initialize all Flask extensions
used across the BahtBuddy backend (e.g., SQLAlchemy, Migrate, etc.).
"""

# 🧩 Import the extensions you plan to use
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 🧠 Create the global extension instances
# These objects are initialized here, and later “linked” to the app in __init__.py

# Database ORM (SQLAlchemy)
db = SQLAlchemy()

# Database migrations (optional but recommended for production)
migrate = Migrate()

# Cross-Origin Resource Sharing (optional, for frontend API calls)
cors = CORS()

# ⚙️ Helper function (optional): initialize all extensions in one call
def init_extensions(app):
    """
    Initializes all Flask extensions with the given Flask app instance.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    print("[BahtBuddy] Flask extensions initialized successfully.")
