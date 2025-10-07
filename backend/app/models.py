from .extensions import db
from decimal import Decimal

# Example money column (works on SQLite & other DBs)
Money = db.Numeric(14, 2, asdecimal=True)