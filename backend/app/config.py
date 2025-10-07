import os

class Config:
    # SQLite DB at backend/instance/bahtbuddy.db (portable, no absolute paths)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.getcwd(), "instance", "bahtbuddy.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
