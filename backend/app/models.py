from .extensions import db

class _Bootstrap(db.Model):
    __tablename__ = "bootstrap_check"
    id = db.Column(db.Integer, primary_key=True)
