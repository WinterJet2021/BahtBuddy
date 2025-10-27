"""
main.py

Personal finance management system with double-entry bookkeeping.
Provides functions for managing accounts, transactions, budgets,
and financial reports following double-entry accounting principles.

Created by Chirayu Sukhum (Tuey) and Thanakrit Punyasuntontamrong (Pass)
Updated for deployment, October 2025
"""

import csv
import json
from typing import Any, Dict, List, Optional, Tuple

import database as db
from validation import ymd, ym, amount_pos, account_type_valid

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

DEFAULT_TRANSACTION_LIMIT = 200
DEFAULT_TRANSACTION_OFFSET = 0

# Chart of Accounts template for Thai banking/finance context
DEFAULT_COA: List[Tuple[str, str]] = [
    # Assets (cash/banks/e-wallets)
    ("Cash", "asset"),
    ("Bank - KBank", "asset"),
    ("Bank - SCB", "asset"),
    ("Bank - Krungthai (KTB)", "asset"),
    ("Bank - Krungsri (BAY)", "asset"),
    ("Bank - Bangkok Bank (BBL)", "asset"),
    ("Bank - TMBThanachart (TTB)", "asset"),
    ("Bank - UOB Thailand", "asset"),
    ("Bank - CIMB Thai", "asset"),
    ("Bank - KKP", "asset"),
    ("Bank - GSB", "asset"),
    ("Bank - Other", "asset"),
    ("Wallet - TrueMoney", "asset"),
    ("Wallet - Rabbit LINE Pay", "asset"),
    ("Wallet - AirPay", "asset"),
    ("Wallet - PromptPay", "asset"),
    ("Wallet - PayPal", "asset"),
    ("Wallet - Alipay", "asset"),
    ("Wallet - WeChat Pay", "asset"),
    ("Wallet - ShopeePay", "asset"),
    ("Wallet - GrabPay", "asset"),
    ("Wallet - Other", "asset"),
    # Liabilities (credit cards)
    ("Credit Card - KBank", "liability"),
    ("Credit Card - SCB", "liability"),
    ("Credit Card - Krungsri (BAY/FirstChoice)", "liability"),
    ("Credit Card - KTC", "liability"),
    ("Credit Card - BBL", "liability"),
    ("Credit Card - UOB", "liability"),
    ("Credit Card - AEON", "liability"),
    ("Credit Card - Citi", "liability"),
    ("Credit Card - Other", "liability"),
    # Income
    ("Salary", "income"),
    ("Allowance", "income"),
    ("Freelance / Side Income", "income"),
    ("Interest / Dividends", "income"),
    ("Gifts / Other Income", "income"),
    ("Refunds / Reimbursements", "income"),
    ("Sale of Assets", "income"),
    ("Tax Refund", "income"),
    ("Bonuses / Commissions", "income"),
    ("Investment Income", "income"),
    ("Rental Income", "income"),
    ("Royalties", "income"),
    ("Grants / Scholarships", "income"),
    ("Pension / Retirement", "income"),
    ("Insurance Payouts", "income"),
    ("Lottery / Gambling Winnings", "income"),
    ("Crowdfunding / Donations", "income"),
    ("Cashback / Rewards", "income"),
    ("Selling Personal Items", "income"),
    ("Other Miscellaneous Income", "income"),
    # Expenses (common Thai categories)
    ("Food & Dining", "expense"),
    ("Transportation", "expense"),
    ("Rent", "expense"),
    ("Utilities", "expense"),
    ("Groceries", "expense"),
    ("Shopping", "expense"),
    ("Health & Fitness", "expense"),
    ("Entertainment", "expense"),
    ("Travel", "expense"),
]

# -----------------------------------------------------------------------------
# Database Initialization Functions
# -----------------------------------------------------------------------------

def init() -> Dict[str, bool]:
    """Initialize the database schema and tables."""
    try:
        db.init_db()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def init_coa_default() -> Dict[str, Any]:
    """Initialize chart of accounts with default template."""
    try:
        added = db.bulk_insert_accounts(DEFAULT_COA)
        return {"ok": True, "added": int(added)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def init_coa_from_file(path: str) -> Dict[str, Any]:
    """Initialize chart of accounts from a CSV or JSON file."""
    try:
        if path.lower().endswith(".csv"):
            rows = _load_accounts_from_csv(path)
        else:
            rows = _load_accounts_from_json(path)
        if not rows:
            return {"ok": False, "error": "No valid accounts found in file."}
        added = db.bulk_insert_accounts(rows)
        return {"ok": True, "added": int(added)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _load_accounts_from_csv(path: str) -> List[Tuple[str, str]]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2 and account_type_valid(row[1]):
                rows.append((row[0], row[1]))
    return rows

def _load_accounts_from_json(path: str) -> List[Tuple[str, str]]:
    rows = []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        name, acc_type = item.get("name"), item.get("type")
        if name and account_type_valid(acc_type):
            rows.append((name, acc_type))
    return rows

def get_accounts() -> Dict[str, Any]:
    """Retrieve all accounts from the database."""
    try:
        rows = db.get_accounts()
        items = [
            {"account_id": r[0], "name": r[1], "type": r[2], "status": r[3]}
            for r in rows
        ]
        return {"ok": True, "items": items}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# -----------------------------------------------------------------------------
# Opening Balance Functions
# -----------------------------------------------------------------------------

def set_opening_balance(account_id: int, amount: float, date: str) -> Dict[str, Any]:
    """Set or update the opening balance for an account."""
    if not db.account_exists(account_id):
        return {"ok": False, "error": "Account does not exist."}
    if not ymd(date) or not amount_pos(amount):
        return {"ok": False, "error": "Invalid opening balance input."}
    db.upsert_opening_balance(account_id, float(amount), date)
    return {"ok": True}

# -----------------------------------------------------------------------------
# Transaction Functions (Double-Entry Bookkeeping)
# -----------------------------------------------------------------------------

def add_transaction(date: str, amount: float, debit_id: int, credit_id: int, notes: str = "") -> Dict[str, Any]:
    """Add a double-entry transaction."""
    if debit_id == credit_id:
        return {"ok": False, "error": "Debit and credit accounts must differ."}
    if not (db.account_exists(debit_id) and db.account_exists(credit_id)):
        return {"ok": False, "error": "One or both accounts do not exist."}
    if not ymd(date) or not amount_pos(amount):
        return {"ok": False, "error": "Invalid date or amount."}
    db.insert_txn(date, float(amount), debit_id, credit_id, notes or "")
    return {"ok": True}

def modify_transaction(txn_id: int, **fields: Any) -> Dict[str, Any]:
    """Modify an existing transaction."""
    clean: Dict[str, Any] = {}
    if "amount" in fields and not amount_pos(fields["amount"]):
        return {"ok": False, "error": "Invalid amount."}
    if "date" in fields and not ymd(fields["date"]):
        return {"ok": False, "error": "Invalid date."}
    if "debit_account_id" in fields and "credit_account_id" in fields:
        if fields["debit_account_id"] == fields["credit_account_id"]:
            return {"ok": False, "error": "Debit and credit must differ."}
    db.update_txn(txn_id, **fields)
    return {"ok": True}

def delete_transaction(txn_id: int) -> Dict[str, bool]:
    """Delete a transaction."""
    db.delete_txn(txn_id)
    return {"ok": True}

def search_transactions(src_account_id=None, dst_account_id=None, date_from=None, date_to=None, limit=DEFAULT_TRANSACTION_LIMIT, offset=DEFAULT_TRANSACTION_OFFSET) -> Dict[str, Any]:
    """Search transactions with filters."""
    rows = db.search_txns(src_account_id, dst_account_id, date_from, date_to, limit, offset)
    items = [
        {
            "txn_id": r[0],
            "date": r[1],
            "amount": float(r[2]),
            "debit_account_id": r[3],
            "credit_account_id": r[4],
            "notes": r[5],
        }
        for r in rows
    ]
    return {"ok": True, "items": items}

def get_balance(account_id: int, date_to: Optional[str] = None) -> Dict[str, Any]:
    """Calculate balance for a given account."""
    if not db.account_exists(account_id):
        return {"ok": False, "error": "Account does not exist."}
    balance = db.account_balance(account_id, date_to)
    return {"ok": True, "balance": float(balance)}

# -----------------------------------------------------------------------------
# Budget Management
# -----------------------------------------------------------------------------

def create_or_update_budget(period: str, category: str, amount: float) -> Dict[str, Any]:
    """Create or update a monthly budget."""
    if not ym(period):
        return {"ok": False, "error": "Invalid period format (YYYY-MM)."}
    if not amount_pos(amount):
        return {"ok": False, "error": "Invalid amount."}
    db.upsert_budget(period, category, float(amount))
    return {"ok": True}

def budget_report(period: str) -> Dict[str, Any]:
    """Generate a budget vs actual spending report."""
    budgets = dict(db.get_budgets(period))
    actuals = db.actuals_by_category(period)
    categories = sorted(set(budgets) | set(actuals))
    rows = []
    for cat in categories:
        b = float(budgets.get(cat, 0.0))
        a = float(actuals.get(cat, 0.0))
        variance = b - a
        pct = (a / b * 100.0) if b > 0 else None
        rows.append({
            "category": cat,
            "budget": b,
            "actual": a,
            "variance": variance,
            "pct_of_budget": pct,
        })
    rows.sort(key=lambda x: x["variance"])
    return {"ok": True, "rows": rows}

# -----------------------------------------------------------------------------
# Runtime Entry (for .exe / CLI use)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("🚀 Starting BahtBuddy backend...")
    try:
        result = init()
        if result.get("ok"):
            print("✅ Database initialized successfully.")
            coa_result = init_coa_default()
            if coa_result.get("ok"):
                print(f"📘 Default Chart of Accounts loaded ({coa_result.get('added', 0)} accounts).")
            else:
                print("⚠️ Chart of Accounts initialization failed:", coa_result.get("error"))
            print("💾 BahtBuddy is ready to use.")
        else:
            print("⚠️ Database initialization failed:", result.get("error"))
    except Exception as e:
        print("❌ Startup error:", e)
    input("\nPress Enter to exit...")
