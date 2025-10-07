from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ----------------------------
# Table: accounts
# ----------------------------
class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='active')

    def __repr__(self):
        return f"<Account {self.name} ({self.type})>"

# ----------------------------
# Table: opening_balances
# ----------------------------
class OpeningBalance(db.Model):
    __tablename__ = 'opening_balances'
    balance_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(50), nullable=False)

# ----------------------------
# Table: transactions
# ----------------------------
class Transaction(db.Model):
    __tablename__ = 'transactions'
    txn_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    debit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    credit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    notes = db.Column(db.String(200))

# ----------------------------
# Table: budgets
# ----------------------------
class Budget(db.Model):
    __tablename__ = 'budgets'
    budget_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20), nullable=False)

# ----------------------------
# Table: reports
# ----------------------------
class Report(db.Model):
    __tablename__ = 'reports'
    report_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)