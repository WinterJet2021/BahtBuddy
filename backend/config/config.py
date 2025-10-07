# backend/config/config.py
import os

# points to .../BahtBuddy/backend
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BACKEND_DIR, "instance", "bahtbuddy.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
